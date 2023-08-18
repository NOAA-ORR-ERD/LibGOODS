import requests
import os
import s3fs
import datetime
from libgoods import utilities
import pandas as pd
import numpy as np

'''
Notes on COOPS naming and aggregations:

Nowcast and forecast files are created four times a day. Output is hourly in 
individual files. So each update generates some number of nowcast files and forecast files
The update cycle time will be the last model output timestep in the nowcast 
files and the first timestep in the forecast files

nos.OFS.fields.nHHH.YYYYMMDD.tCCz.nc or 
glos.OFS.fields.nHHH.YYYYMMDD.tCCz.nc (Great Lakes models)

OFS = model name, eg. "DBOFS"
nHHH = nowcast number, eg. n001-n006 or "nowcast" for old POM models
CC = update hour, e.g. 00,06...

Different models have different update cycles:
FVCOM (non-Great Lakes): 3,9,15,21
ROMS: 0,6,12,18
FVCOM (Great Lakes): 0,6,12,18
Great Lakes POM: 0,6,12,18
Other POM: 5,11,17,23

So to make a time series, use subsequent nowcasts updates strung together sequentially
by update date/time then by individual nowcast files.

The trick is, there is inconsistency between number of nowcast files among models.
Here's the lowdown:
FVCOM: nowcast numbering from 000-->006 with overlap between 6 and 0
ROMS (except GOMOFS): nowcast numbering from 001-->006 with no overlap
GOMOFS ROMS: nowcast 003 and 006 only - ouptut is 3 hourly, no overlap
POM models: one nowcast file "nowcast" in file name, 6 hours, no overlap between nowcasts

Then append the forecast that is the same update cycle as the most recent nowcast
'''

coops_ofs = {'NGOFS2':{'output_ts':3,'fc':[0,48],'nc':[0,3],'update_freq':6,'cycles':[3,9,15,21]},
             'CREOFS':{'output_ts':1,'fc':[0,48],'nc':[0,1,2,3,4,5],'update_freq':6,'cycles':[3,9,15,21]},
             'DBOFS':{'output_ts':1,'fc':[1,48],'nc':[1,2,3,4,5,6],'update_freq':6,'cycles':[0,6,12,18]},
             'LMHOFS':{'output_ts':1,'fc':[1,120],'nc':[0,1,2,3,4,5],'update_freq':6,'cycles':[0,6,12,18]},
             'CIOFS':{'output_ts':1,'fc':[1,48],'nc':[1,2,3,4,5,6],'update_freq':6,'cycles':[0,6,12,18]},
             'WCOFS':{'output_ts':3,'fc':[3,72],'nc':[3,6,9,12,15,18,21,24],'update_freq':24,'cycles':[3]},
            }

def get_coops_flist_for_download(model_id,start,end):
    '''AWS S3 bucket has files sorted by model then into individual months
    '''
    nc_list = []
    fc_list = []
    
    aws_root = 's3://noaa-nos-ofs-pds/'
    
    #add some buffer for the file search
    start = (start-datetime.timedelta(hours=coops_ofs[model_id]['update_freq'])) #6 hours is the typical update cycle
    end = (end+datetime.timedelta(hours=coops_ofs[model_id]['update_freq']))
    ts = pd.date_range(start,end).strftime('%Y%m')
    dirs_to_search = np.unique(ts)

    fs = s3fs.S3FileSystem(anon=True)
    temp_nc_list = []
    temp_fc_list = []
    
    #select all nowcast files that don't overlap
    for d in dirs_to_search:
        url = aws_root + model_id.lower() + '/netcdf/' + d + '/'
        flist = fs.ls(url)
        for nc in coops_ofs[model_id]['nc']: 
            temp_nc_list.extend([f for f in flist if 'fields.n' + str(nc).zfill(3) in f])
        temp_fc_list.extend([f for f in flist if 'fields.f' in f] )
    
    #keep nowcast files in time range
    nc_list = []
    for f in temp_nc_list:
        dt = utilities.file2dt(f)        
        if (dt>=start and dt<=end):
            nc_list.append(f)
            
    nc_list.sort(key=lambda x: x.split('.')[4]+x.split('.')[5])
    
    #if the start date is wholly in the forecast range this will tank here (empty list)
    if utilities.file2dt(nc_list[-1]) < end:
        fc_list = []
        date_cycle = nc_list[-1].split('.')[4]+ '.' + nc_list[-1].split('.')[5]
        for f in temp_fc_list:
            try:
                f.index(date_cycle)
                fc_list.append(f)
            except ValueError:
                pass
             
        
    return nc_list + fc_list
                
        
def download_from_coops_ofs(fnames,out_dir='temp_files'):
    '''
    NOS OFS are available in an AWS S3 bucket at:
    https://noaa-nos-ofs-pds.s3.amazonaws.com/index.html

    You can browse around and see what’s there in a big heap of files. To generate a list of files to download (a time series) you can leverage some of the code in model_catalogs to get the list of files.

    Parameters
    ----------
    
    fnames : list of filenames (str)
    
    '''
    
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    aws_url = 'https://noaa-nos-ofs-pds.s3.amazonaws.com/'
    newfilenames = []
    for fname in fnames:
        
        out_file =  os.path.join(out_dir,fname.split('/')[-1])
        if os.path.exists(out_file):
            print('Already downloaded', fname)
        else:
            if fname.startswith('noaa-nos-ofs-pds'):
                url = aws_url + fname.split('pds/')[-1]
            else: #filenames from model_catalogs
                yyyymmdd = fname.split('.')[4]      
                model_id = fname.split('.')[1]
                url = aws_url + model_id + '/netcdf/' + yyyymmdd[0:6] + '/' + fname
            print(url)
            r = requests.get(url)
            #resp = http.request("GET", url, preload_content=False)
            
            if r.headers['Content-Type'] == 'application/xml':
                print(r.content)
            else:
                
                with open(out_file,'wb') as f:
                    f.write(r.content)
        newfilenames.append(out_file)            
    return newfilenames