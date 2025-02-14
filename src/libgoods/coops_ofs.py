import datetime
import fnmatch
import os
import re
from dataclasses import dataclass

import numpy as np
import pandas as pd
import requests
import s3fs
from netCDF4 import Dataset
from siphon.catalog import TDSCatalog


# NOTE: maybe this can be merged with the model Metadata class -- or not
#       This is really about what we need to know to download the files, etc
#       Not what we want to present to users -- but id the a reason to keep them separate?
#       Maybe not
@dataclass()
class ModelInfo:
    identifier: str = ""
    name: str = ""
    update_cycle: int = 6

model_ids = [
    'WCOFS', 'SSCOFS', 'NGOFS2', 'CBOFS', 'TBOFS', 'DBOFS', 'GOMOFS', 'CIOFS', 'SFBOFS',
    'LEOFS', 'LMHOFS', 'LOOFS', 'LSOFS'
]

OFS_INFO = {ID: ModelInfo(ID, ID + "model") for ID in model_ids}
OFS_INFO['WCOFS'].update_cycle = 24

"""
Notes on COOPS naming and aggregations:

Nowcast and forecast files are created four times a day. Output is hourly in
individual files. So each update generates some number of nowcast files and forecast files
The update cycle time will be the last model output timestep in the nowcast
files and the first timestep in the forecast files

Format prior to Aug2024
nos.{OFS}.fields.nHHH.YYYYMMDD.tCCz.nc or

Post Aug2024
{OFS}.tCCz.YYYYMMDD.fields.nHHH.nc or

!!!! Time series that require both old and new formats NOT supported!!!!!!!!

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

def get_tds_flist(model_info, start, end, file_type='2ds', old_name_format=False, tds='coops'):
    """
    COOPS TDS has files sorted by model then into year/month/day
            file_type: 2ds for 2d, fields for 3d

    Parameters
    ----------
    model_info: str
        ID of the model, should be one of what's in OFS_INFO dict
        (`coops_ofs.OFS_INFO.keys()` to see what's there.)

    start : datetime
        The start of the time you want

    end : datetime
        The end of th time you want

    file_type='2ds' : str
        whether you want the 2D or 3D files. Options: '2ds' for 2D, 'fields' for 3D

    old_name_format=False: bool
        whether to use the old name format (before Aug 2024)

    tds='coops': str
        which TDS service it is: 'coops' or 'ncei'

    Returns
    -------
    list of filenames on the TDS server.

    """

    nc_list = []
    fc_list = []

    # add some buffer for the file search (6 hrs the typical update cycle)
    buffer = datetime.timedelta(hours=6)
    start_b = (start - buffer)
    end_b = (end + buffer)
    if tds == 'coops':
        ts = pd.date_range(start_b, end_b).strftime('%Y/%m/%d')
        thredds_root = 'https://opendap.co-ops.nos.noaa.gov/thredds/'
    elif tds == 'ncei':
        ts = pd.date_range(start_b, end_b).strftime('%Y/%m')
        thredds_root = 'https://ncei.noaa.gov/thredds/'

    dirs_to_search = np.unique(ts)

    # select all nowcast files that don't overlap
    for d in dirs_to_search:
        if tds == 'coops':
            url = thredds_root + 'catalog/NOAA/' + model_info.identifier.upper(
            ) + '/MODELS/' + d + '/catalog.xml'
        else:
            url = thredds_root + 'catalog/model-' + model_info.identifier.lower(
            ) + '-files/' + d + '/catalog.xml'

        try:
            cat = TDSCatalog(url)
        except:
            print('Could not open TDS catalog:', url)
            continue

        dsc = list(cat.datasets.values())
        flist = [ds.access_urls['OPENDAP'] for ds in dsc]

        if old_name_format:
            flist = [
                f for f in flist
                if f.split('/')[-1].startswith('nos.') and file_type in f.split('/')[-1]
            ]
        else:
            flist = [
                f for f in flist
                if not f.split('/')[-1].startswith('nos.') and file_type in f.split('/')[-1]
            ]
        if len(flist) == 0:
            print('No files of type', file_type, 'found')
            raise KeyError

        # separate into nowcast/forecast lists and exclude 0th files (overlap)
        nc_list.extend([f for f in flist if re.search(".n[0-9]{3}.", f) and ".n000" not in f])
        fc_list.extend([f for f in flist if re.search(".f[0-9]{3}.", f) and ".f000" not in f])

    # this directory crawling results in duplicates for some reason
    nc_list = list(np.unique(nc_list))
    fc_list = list(np.unique(fc_list))

    flist = prune_files_to_daterange(nc_list,
                                     fc_list,
                                     start,
                                     end,
                                     model_info.update_cycle)

    return flist


def get_aws_flist(model_info, start, end, file_type='2ds', old_name_format=False):
    """
    AWS S3 bucket has files sorted by model then into year/month
        file_type: '2ds' for 2d, 'fields' for 3d
    """

    nc_list = []
    fc_list = []

    aws_root = 's3://noaa-nos-ofs-pds/'

    # add some buffer for the file search (6 hrs the typical update cycle)
    buffer = datetime.timedelta(hours=6)
    start_b = (start - buffer)
    end_b = (end + buffer)
    ts = pd.date_range(start_b, end_b).strftime('%Y/%m/%d')
    dirs_to_search = np.unique(ts)

    fs = s3fs.S3FileSystem(anon=True)

    # select all nowcast files that don't overlap
    for d in dirs_to_search:
        url = aws_root + model_info.identifier.lower() + '/netcdf/' + d + '/'
        if old_name_format:
            flist = [
                f for f in fs.ls(url)
                if f.split('/')[-1].startswith('nos.') and file_type in f.split('/')[-1]
            ]
        else:
            flist = [
                f for f in fs.ls(url)
                if not f.split('/')[-1].startswith('nos.') and file_type in f.split('/')[-1]
            ]
            
        if len(flist) != 0:
            #separate into nowcast/forecast lists and exclude 0th files (overlap)
            nc_list.extend([f for f in flist if re.search(".n[0-9]{3}.", f) and ".n000" not in f])
            fc_list.extend([f for f in flist if re.search(".f[0-9]{3}.", f) and ".f000" not in f])
            
            
    if len(nc_list) + len(fc_list) == 0:        
        print('No files of type', file_type, 'found')
        raise KeyError

    flist = prune_files_to_daterange(nc_list, fc_list, start, end, model_info.update_cycle)

    return flist


def get_local_flist(model_info, start, end, local_dir, file_type='2ds'):
    '''
    Assumes all files are in one directory for one OFS
    '''

    nc_list = []
    fc_list = []

    flist = os.listdir(local_dir)  #pass in search string
    flist = [f for f in flist if file_type in f]

    #separate into nowcast/forecast lists and exclude 0th files (overlap)
    nc_list.extend([f for f in flist if re.search(".n[0-9]{3}.", f) and ".n000" not in f])
    fc_list.extend([f for f in flist if re.search(".f[0-9]{3}.", f) and ".f000" not in f])

    flist = prune_files_to_daterange(nc_list, fc_list, start, end, model_info.update_cycle)

    return flist


def get_zarr_url(model_info,check_exists=False):
    """
    Gives the url for the "best timeseries" kerchunked zarr file at:
    https://noaa-nodd-kerchunk-pds.s3.amazonaws.com/
    Exameple URL for WCOFs:
    s3://noaa-nodd-kerchunk-pds/nos/wcofs/wcofs.fields.best.nc.zarr
    """
    root_url = 's3://noaa-nodd-kerchunk-pds/nos/'
    model_url = root_url + model_info.identifier.lower() + '/' + model_info.identifier.lower(
    ) + '.fields.best.nc.zarr'
    fs = s3fs.S3FileSystem(anon=True)
    if check_exists:
        try:
            fmatch = fs.ls(model_url)
            if len(fmatch) == 1:
                flist = model_url
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            print('zarr file not found on server')
            flist = None
    else:
        flist = model_url

    return flist


def get_ioos_tds_agg_url(model_info):
    """
    Gives the url for the "best timeseries" TDS url from IOOS server

    """
    root_url = 'https://tds.ioos.us/thredds/dodsC/ioos/ofs/'

    model_url = root_url + model_info.identifier.lower(
    ) + '/' + 'forecast/fields/' + model_info.identifier + '_Forecast_Fields_best.ncd'

    try:
        ds = Dataset(model_url)
        flist = model_url
    except:
        print('Aggregation not found on IOOS server')
        flist = None

    return flist


def download_from_aws(model_info, fnames, out_dir='files', temp_dir=None):
    """
    NOS OFS are available in an AWS S3 bucket at:
    https://noaa-nos-ofs-pds.s3.amazonaws.com/index.html

    Parameters
    ----------

    fnames : list of filenames (str)

    """
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    if temp_dir is not None:
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)

    aws_url = 'https://noaa-nos-ofs-pds.s3.amazonaws.com/'
    newfilenames = []
    for fname in fnames:
        fpath = os.path.join(out_dir, fname.split('/')[-1])
        if os.path.exists(fpath):
            print('Already downloaded', fname)
        else:
            if temp_dir is not None:
                fpath = os.path.join(temp_dir, fname.split('/')[-1])
                if os.path.exists(fpath):
                    print('Already downloaded', fname)
                else:
                    print('Downloading:', fname)
                    url = aws_url + fname.split('pds/')[-1]
                    r = requests.get(url)
                    # resp = http.request("GET", url, preload_content=False)

                    if r.headers['Content-Type'] == 'application/xml':
                        print(r.content)
                    else:
                        with open(fpath, 'wb') as f:
                            f.write(r.content)
                    newfilenames.append(fpath)

    return newfilenames


def file2dt(filename, tshift, coops_fname_format='new'):
    """
    Return Timestamp of NOAA OFS filename based on naming convention.
    This is for OFS output with 1 timestep per file (everything but NYOFS)

    Parameters
    ----------
    filename : str
        Filename for which to decipher datetime.
    tshift : int
        Update cycle for COOPS OFS -- typically 6 but WCOFS is 24
    coops_fname_format : str
        Either "old" or "new" based on COOPS naming conventions (see notes in class)
    Returns
    -------
    Timestamp
        datetime of the time(s) in the file.

    Examples
    --------
    >>> fname = 'nos.cbofs.fields.n001.20220701.t00z.nc' #old format
    >>> file2dt(fname)
    Timestamp('2022-06-30 19:00:00')
    """

    if coops_fname_format == 'new':
        ofs = filename.split('.')[0].upper()
    else:
        ofs = filename.split('.')[1].upper()
    # read in date from filename
    date = pd.to_datetime(filename, format="%Y%m%d", exact=False)  # has time 00:00

    # pull timing cycle from filename
    regex = re.compile(".t[0-9]{2}z.")
    cycle = int(regex.findall(filename)[0][2:4])

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


def prune_files_to_daterange(nc_list, fc_list, start, end, update_cycle):

    if len(nc_list) > 1:
        test_it = nc_list[0].split('.')[-2]  #look at last part of fname to check old/newformat
    elif len(fc_list) > 1:
        test_it = fc_list[0].split('.')[-2]
    else:
        print('No files found')
        raise IndexError
    try:
        test_it.index('t')
        coops_fname_format = 'old'
    except ValueError:
        coops_fname_format = 'new'

    # keep nowcast/forecast files in time range
    pruned_nc_list = []
    pruned_fc_list = []
    pruned_dts = []
    dts = [file2dt(f.split('/')[-1], update_cycle, coops_fname_format) for f in nc_list]

    buffer = datetime.timedelta(
        hours=3
    )  #ideally this buffer should be based on output timestep -- but 3 hours is the least resolution offered so this works

    for f, dt in zip(nc_list, dts):
        if (dt >= start - buffer and dt <= end + buffer):
            pruned_nc_list.append(f)
            pruned_dts.append(dt)

    #remove 0th nowcast if exists
    #pruned_nc_list = [f for f in pruned_nc_list if not fnmatch.fnmatch]

    pruned_nc_list = [x for y, x in sorted(zip(pruned_dts, pruned_nc_list))]

    # if the start date is wholly in the forecast range this will tank here (empty list)
    regex = re.compile(".t[0-9]{2}z.")
    try:
        last_nc_file = pruned_nc_list[-1].split('/')[-1]
        if file2dt(last_nc_file, update_cycle, coops_fname_format) < end:
            cycle = regex.findall(last_nc_file)[0][2:4]
            date = pd.to_datetime(last_nc_file, format="%Y%m%d",
                                  exact=False).strftime("%Y%m%d")
            for f in fc_list:
                if f.find(date + '.t' + cycle + 'z') + f.find('t' + cycle + 'z.' + date) > -1:
                    pruned_fc_list.append(f)
            dts = [
                file2dt(f.split('/')[-1], update_cycle, coops_fname_format)
                for f in pruned_fc_list
            ]
            pruned_fc_list = [x for y, x in sorted(zip(dts, pruned_fc_list))]
    except IndexError:
        print('No nowcast files available')
        no_nowcasts = True
        dts = [file2dt(f.split('/')[-1], update_cycle, coops_fname_format) for f in fc_list]
        sorted_fc_list = [x for y, x in sorted(zip(dts, fc_list))]
        cycle = regex.findall(sorted_fc_list[-1])[0][2:4]
        date = pd.to_datetime(sorted_fc_list[-1], format="%Y%m%d",
                              exact=False).strftime("%Y%m%d")
        for f in sorted_fc_list:
            if f.find(date + '.t' + cycle + 'z') + f.find('t' + cycle + 'z.' + date) > -1:
                pruned_fc_list.append(f)

    return pruned_nc_list + pruned_fc_list
