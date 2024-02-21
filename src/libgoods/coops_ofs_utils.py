import datetime
import os
import pandas as pd
import numpy as np
import fnmatch
import re
import s3fs
from siphon.catalog import TDSCatalog
import requests


"""
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

aws link: https://noaa-nos-ofs-pds.s3.amazonaws.com/index.html
tds link: https://opendap.co-ops.nos.noaa.gov/thredds/catalog/catalog.html
"""

coops_ofs = {
    'NGOFS2': {
        'output_ts': 3,
        'fc': [0, 48],
        'nc': [0, 3],
        'update_freq': 6,
        'cycles': [3, 9, 15, 21]
    },
    'CREOFS': {
        'output_ts': 1,
        'fc': [0, 48],
        'nc': [0, 1, 2, 3, 4, 5],
        'update_freq': 6,
        'cycles': [3, 9, 15, 21]
    },
    'DBOFS': {
        'output_ts': 1,
        'fc': [1, 48],
        'nc': [1, 2, 3, 4, 5, 6],
        'update_freq': 6,
        'cycles': [0, 6, 12, 18]
    },
    'CBOFS': {
        'output_ts': 1,
        'fc': [1, 48],
        'nc': [1, 2, 3, 4, 5, 6],
        'update_freq': 6,
        'cycles': [0, 6, 12, 18]
    },
    'LMHOFS': {
        'output_ts': 1,
        'fc': [1, 120],
        'nc': [0, 1, 2, 3, 4, 5],
        'update_freq': 6,
        'cycles': [0, 6, 12, 18]
    },
    'CIOFS': {
        'output_ts': 1,
        'fc': [1, 48],
        'nc': [1, 2, 3, 4, 5, 6],
        'update_freq': 6,
        'cycles': [0, 6, 12, 18]
    },
    'WCOFS': {
        'output_ts': 3,
        'fc': [3, 72],
        'nc': [3, 6, 9, 12, 15, 18, 21, 24],
        'update_freq': 24,
        'cycles': [3]
    },
}

def file2dt(filename):
    """
    Return Timestamp of NOAA OFS filename based on naming convention. 
    This is for OFS output with 1 timestep per file (everything but NYOFS)

    Parameters
    ----------
    filename : str
        Filename for which to decipher datetime.
        
    Returns
    -------
    Timestamp
        datetime of the time(s) in the file.

    Examples
    --------
    >>> fname = 'nos.cbofs.fields.n001.20220701.t00z.nc'
    >>> file2dt(fname)
    Timestamp('2022-06-30 19:00:00')
    """
    ofs = filename.split('.')[1].upper()
    
    # read in date from filename
    date = pd.to_datetime(filename, format="%Y%m%d",
                          exact=False)  # has time 00:00

    # pull timing cycle from filename
    regex = re.compile(".t[0-9]{2}z.")
    cycle = int(regex.findall(filename)[0][2:4])

    # number of hours in repeat cycle for forecast
    tshift = coops_ofs[ofs]['update_freq']

    # pull hours from filename
    regex = re.compile(".[n,f][0-9]{3}.")
    hour = int(regex.findall(filename)[0][2:-1])

    # calculate hours
    dt = cycle + hour

    # if nowcast file, subtract dt hours
    if fnmatch.fnmatch(filename, "*.n???.*"):
        dt -= tshift

    # construct datetime. dt might be negative.
    date += pd.Timedelta(f"{dt} hours")

    return date.to_pydatetime()

def get_tds_flist(model_id, start, end):
    '''COOPS TDS has files sorted by model then into year/month/day
    '''
    
    nc_list = []
    fc_list = []
    
    # add some buffer for the file search (6 hrs the typical update cycle)
    start = (start - datetime.timedelta(hours=coops_ofs[model_id]['update_freq']))  
    end = (end + datetime.timedelta(hours=coops_ofs[model_id]['update_freq']))
    ts = pd.date_range(start, end).strftime('%Y/%m/%d')
    dirs_to_search = np.unique(ts)
    thredds_root = 'https://opendap.co-ops.nos.noaa.gov/thredds/'
    
    # select all nowcast files that don't overlap
    for d in dirs_to_search:
        url = thredds_root + 'catalog/NOAA/' + model_id.upper() + '/MODELS/' + d + '/catalog.xml'
        try:
            cat = TDSCatalog(url)
        except:
            pass
            
        flist = cat.datasets
        
        for nc in coops_ofs[model_id.upper()]['nc']:
            nc_list.extend(
                [f for f in flist if 'fields.n' + str(nc).zfill(3) in f])
        fc_list.extend([f for f in flist if 'fields.f' in f])
        
    flist = prune_files_to_daterange(nc_list,fc_list,start,end)
    
    return flist

    
def get_aws_flist(model_id, start, end):
    '''AWS S3 bucket has files sorted by model then into year/month
    '''
    nc_list = []
    fc_list = []

    aws_root = 's3://noaa-nos-ofs-pds/'

    # add some buffer for the file search (6 hrs the typical update cycle)
    start = (start - datetime.timedelta(hours=coops_ofs[model_id]['update_freq']))  
    end = (end + datetime.timedelta(hours=coops_ofs[model_id]['update_freq']))
    ts = pd.date_range(start, end).strftime('%Y%m')
    dirs_to_search = np.unique(ts)

    fs = s3fs.S3FileSystem(anon=True)

    # select all nowcast files that don't overlap
    for d in dirs_to_search:
        url = aws_root + model_id.lower() + '/netcdf/' + d + '/'
        flist = fs.ls(url)
        for nc in coops_ofs[model_id]['nc']:
            nc_list.extend(
                [f for f in flist if 'fields.n' + str(nc).zfill(3) in f])
        fc_list.extend([f for f in flist if 'fields.f' in f])

    flist = prune_files_to_daterange(nc_list,fc_list,start,end)
    
    return flist

def prune_files_to_daterange(nc_list,fc_list,start,end):

    # keep nowcast/forecast files in time range
    pruned_nc_list = []
    pruned_fc_list = []
    
    for f in nc_list:
        dt = file2dt(f.split('/')[-1])
        if (dt >= start and dt <= end):
            pruned_nc_list.append(f)

    pruned_nc_list.sort(key=lambda x: x.split('.')[4] + x.split('.')[5] + x.split('.')[3])

    # if the start date is wholly in the forecast range this will tank here (empty list)
    if file2dt(pruned_nc_list[-1]) < end:
        date_cycle = pruned_nc_list[-1].split('.')[4] + '.' + pruned_nc_list[-1].split(
            '.')[5]
        for f in fc_list:
            try:
                f.index(date_cycle)
                pruned_fc_list.append(f)
            except ValueError:
                pass    
        pruned_fc_list.sort(key=lambda x: x.split('.')[4] + x.split('.')[5] + x.split('.')[3])     

    return pruned_nc_list + pruned_fc_list


def get_local_flist(model_id, start, end, local_dir,glob_pattern):
    '''COOPS TDS has files sorted by model then into year/month/day
    '''    
    nc_list = []
    fc_list = []
   
    flist = local_dir.glob(glob_pattern) #pass in search string
    flist = [str(f) for f in flist]    
    for nc in coops_ofs[model_id.upper()]['nc']:
        nc_list.extend(
            [f for f in flist if 'fields.n' + str(nc).zfill(3) in f])
    fc_list.extend([f for f in flist if 'fields.f' in f])
        
    flist = prune_files_to_daterange(nc_list,fc_list,start,end)
    
    return flist
    
def download_from_aws(fnames, out_dir='temp_files'):
    """
    NOS OFS are available in an AWS S3 bucket at:
    https://noaa-nos-ofs-pds.s3.amazonaws.com/index.html

 
    Parameters
    ----------

    fnames : list of filenames (str)

    """

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    aws_url = 'https://noaa-nos-ofs-pds.s3.amazonaws.com/'
    newfilenames = []
    for fname in fnames:
        print(fname)
        out_file = os.path.join(out_dir, fname.split('/')[-1])
        if os.path.exists(out_file):
            print('Already downloaded', fname)
        else:
            if fname.startswith('noaa-nos-ofs-pds'):
                url = aws_url + fname.split('pds/')[-1]
            else:  # filenames from model_catalogs
                yyyymmdd = fname.split('.')[4]
                model_id = fname.split('.')[1]
                url = aws_url + model_id + '/netcdf/' + yyyymmdd[
                    0:6] + '/' + fname
            print(url)
            r = requests.get(url)
            # resp = http.request("GET", url, preload_content=False)

            if r.headers['Content-Type'] == 'application/xml':
                print(r.content)
            else:

                with open(out_file, 'wb') as f:
                    f.write(r.content)
        newfilenames.append(out_file)
    return newfilenames

