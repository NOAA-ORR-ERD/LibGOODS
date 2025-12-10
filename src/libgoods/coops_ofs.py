import datetime
import fnmatch
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path

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
    "WCOFS",
    "SSCOFS",
    "NGOFS2",
    "CBOFS",
    "TBOFS",
    "DBOFS",
    "GOMOFS",
    "CIOFS",
    "SFBOFS",
    "LEOFS",
    "LMHOFS",
    "LOOFS",
    "LSOFS",
]

OFS_INFO = {ID: ModelInfo(ID, ID + "model") for ID in model_ids}
OFS_INFO["WCOFS"].update_cycle = 24

"""
Notes on COOPS naming and aggregations:

Nowcast and forecast files are created four times a day. Output is hourly in
individual files. So each update generates some number of nowcast files and forecast files
The update cycle time will be the last model output timestep in the nowcast
files and the first timestep in the forecast files

Format prior to Aug2024 (ON AWS this format goes through April 2024 - after that only new format)
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


def get_tds_flist(model_id, start, end, file_type="2ds", old_name_format=False, tds="coops"):
    """
    COOPS TDS has files sorted by model then into year/month/day
            file_type: 2ds for 2d, fields for 3d

    Parameters
    ----------
    model_id: str
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
    model_info = OFS_INFO[model_id]

    nc_list = []
    fc_list = []

    # add a generous buffer for the file search (refined later)
    buffer = datetime.timedelta(hours=24)
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
        if tds == "coops":
            url = (
                thredds_root
                + "catalog/NOAA/"
                + model_info.identifier.upper()
                + "/MODELS/"
                + d
                + "/catalog.xml"
            )
        else:
            url = (
                thredds_root
                + "catalog/model-"
                + model_info.identifier.lower()
                + "-files/"
                + d
                + "/catalog.xml"
            )

        try:
            cat = TDSCatalog(url)
        # what exception would we get here??
        except Exception as err:
            msg = f"Could not open TDS catalog:{url}\n{err}"
            logging.warning(msg)
            print(msg)
            continue

        dsc = list(cat.datasets.values())
        flist = [ds.access_urls["OPENDAP"] for ds in dsc]

        if old_name_format:
            flist = [
                f
                for f in flist
                if f.split("/")[-1].startswith("nos.") and file_type in f.split("/")[-1]
            ]
        else:
            flist = [
                f
                for f in flist
                if not f.split("/")[-1].startswith("nos.") and file_type in f.split("/")[-1]
            ]
        if len(flist) == 0:
            print("No files of type", file_type, "found")
            raise KeyError

        # separate into nowcast/forecast lists and exclude 0th files (overlap)
        nc_list.extend([f for f in flist if re.search(".n[0-9]{3}.", f) and ".n000" not in f])
        fc_list.extend([f for f in flist if re.search(".f[0-9]{3}.", f) and ".f000" not in f])

    # this directory crawling results in duplicates for some reason
    nc_list = list(np.unique(nc_list))
    fc_list = list(np.unique(fc_list))

    flist = prune_files_to_daterange(nc_list, fc_list, start, end, model_info.update_cycle)

    return flist


def get_aws_flist(model_id, start, end, file_type="2ds", old_name_format=False):
    """
    AFTER 2024/11/19:
    AWS S3 bucket has files sorted by model then into year then month then day
        file_type: '2ds' for 2d, 'fields' for 3d
    !!!!!!For dates prior to this use the get_aws_flist_year method!!!!!!
    """

    nc_list = []
    fc_list = []

    aws_root = 's3://noaa-nos-ofs-pds/'
    #add a generous buffer for the file search (refined later)
    # NOTE: this is going out too far
    #        -- to the next day, which then crashes...
    #       that's getting caught later by a try: except, but
    #       maybe we should be smarter.
    # This could, instead, get a listing, to see what's actually available
    model_info = OFS_INFO[model_id]
    buffer = datetime.timedelta(hours=72)
    start_b = (start - buffer)
    end_b = (end + buffer)
    ts = pd.date_range(start_b, end_b).strftime('%Y/%m/%d')
    dirs_to_search = np.unique(ts)

    fs = s3fs.S3FileSystem(anon=True)

    # select all nowcast files that don't overlap
    for d in dirs_to_search:
        url = aws_root + model_info.identifier.lower() + "/netcdf/" + d + "/"
        try:
            listing = fs.ls(url)
        except FileNotFoundError:
            logging.debug(f"url not found: {url}")
            # could probably break out, but maybe not in order?
            continue
        if old_name_format:
            raise Exception("using the old name format -- why??")
            flist = [
                f
                for f in listing
                # put this logic somewhere else??
                if f.split("/")[-1].startswith("nos.") and file_type in f.split("/")[-1]
            ]
        else:
            flist = [
                f
                for f in listing
                if not f.split("/")[-1].startswith("nos.") and file_type in f.split("/")[-1]
            ]
        if len(flist) != 0:
            # separate into nowcast/forecast lists and exclude 0th files (overlap)
            nc_list.extend([f for f in flist if re.search(".n[0-9]{3}.", f) and ".n000" not in f])
            fc_list.extend([f for f in flist if re.search(".f[0-9]{3}.", f) and ".f000" not in f])

    if len(nc_list) + len(fc_list) == 0:
        print("No files of type", file_type, "found")
        raise KeyError

    flist = prune_files_to_daterange(nc_list, fc_list, start, end, model_info.update_cycle)

    return flist

def get_aws_flist_all(model_id, file_type="2ds"):
    """
    Get the aws paths for all the nowcast files
    Files are ordered in folders by year/month until 11/2024
    After that ordered by year/month/day
    New file name convention from 05/2024
    model_id: str
        ID of the model, should be one of what's in OFS_INFO dict
        (`coops_ofs.OFS_INFO.keys()` to see what's there.)

    file_type='2ds' : str
        whether you want the 2D or 3D files. Options: '2ds' for 2D, 'fields' for 3D
    """

    nc_list = []

    aws_root = 's3://noaa-nos-ofs-pds/'
    model_info = OFS_INFO[model_id]


    fs = s3fs.S3FileSystem(anon=True)


    url = aws_root + model_info.identifier.lower() + "/netcdf/"

    for dirpath, dirnames, filenames in fs.walk(url):

        for f in filenames:
            fpath = f"{dirpath}/{f}"
            if file_type in f.split("/")[-1] and re.search(".n[0-9]{3}.", f) and ".n000" not in f:
                nc_list.append(str(fpath))
                print(f"Adding file: {fpath}")

    nc_list_sorted = prune_files_to_daterange(nc_list, [],
                                              start=None,
                                              end=None,
                                              update_cycle=model_info.update_cycle)

    return nc_list_sorted


def get_local_flist(model_id, local_dir, start=None, end=None, file_type="2ds"):
    """
    Assumes all files are in one directory for one OFS
    """
    model_info = OFS_INFO[model_id]
    nc_list = []
    fc_list = []

    model_dir = Path(local_dir, model_info.identifier.lower(), "netcdf")

    flist = []
    for f in model_dir.rglob("*.nc"):
        if file_type in str(f):
            flist.append(str(f))

    # separate into nowcast/forecast lists and exclude 0th files (overlap)
    nc_list.extend([f for f in flist if re.search(".n[0-9]{3}.", f) and ".n000" not in f])
    fc_list.extend([f for f in flist if re.search(".f[0-9]{3}.", f) and ".f000" not in f])

    flist_out = prune_files_to_daterange(nc_list, fc_list, start, end, model_info.update_cycle)

    return flist_out


def get_zarr_url(model_id, check_exists=False):
    """
    Gives the url for the "best timeseries" kerchunked zarr file at:
    https://noaa-nodd-kerchunk-pds.s3.amazonaws.com/
    Exameple URL for WCOFs:
    s3://noaa-nodd-kerchunk-pds/nos/wcofs/wcofs.fields.best.nc.zarr
    """
    model_info = OFS_INFO[model_id]
    root_url = "s3://noaa-nodd-kerchunk-pds/nos/"
    model_url = (
        root_url
        + model_info.identifier.lower()
        + "/"
        + model_info.identifier.lower()
        + ".fields.best.nc.zarr"
    )
    fs = s3fs.S3FileSystem(anon=True)
    if check_exists:
        try:
            fmatch = fs.ls(model_url)
            if len(fmatch) == 1:
                flist = model_url
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            print("zarr file not found on server")
            flist = None
    else:
        flist = model_url

    return flist


def get_ioos_tds_agg_url(model_id):
    """
    Gives the url for the "best timeseries" TDS url from IOOS server

    """
    model_info = OFS_INFO[model_id]
    root_url = "https://tds.ioos.us/thredds/dodsC/ioos/ofs/"

    model_url = (
        root_url
        + model_info.identifier.lower()
        + "/"
        + "forecast/fields/"
        + model_info.identifier
        + "_Forecast_Fields_best.ncd"
    )

    try:
        ds = Dataset(model_url) # noqa:F841
        flist = model_url
    # fixme: what ecxeption(s) might we get here???
    except:  # noqa:E722
        print("Aggregation not found on IOOS server")
        flist = None

    return flist


def download_from_aws(model_id, fnames, out_dir="files", temp_dir=None):
    """
    NOS OFS are available in an AWS S3 bucket at:
    https://noaa-nos-ofs-pds.s3.amazonaws.com/index.html
    https://noaa-nos-ofs-pds.s3.amazonaws.com/index.html
    Parameters
    ----------

    fnames : list of filenames (str)

    """
    # model_info = OFS_INFO[model_id]
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    if temp_dir is not None:
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)

    aws_url = "https://noaa-nos-ofs-pds.s3.amazonaws.com/"
    newfilenames = []

    for fname in fnames:

        fpath = os.path.join(out_dir, fname.split("/")[-1])
        newfilenames.append(fpath)

        if os.path.exists(fpath):
            logging.info(f"Already downloaded, {fname}")
            print('Already downloaded', fname)
            continue
        else:
            if temp_dir is not None:
                fpath = os.path.join(temp_dir, fname.split("/")[-1])
                if os.path.exists(fpath):
                    logging.info(f"Already downloaded, {fname}")
                    print("Already downloaded", fname)
                    continue

        print("Downloading:", fname)
        url = aws_url + fname.split("pds/")[-1]
        r = requests.get(url)
        # resp = http.request("GET", url, preload_content=False)

        if r.headers["Content-Type"] == "application/xml":
            print(r.content)
        else:
            with open(fpath, "wb") as f:
                f.write(r.content)

    return newfilenames


def file2dt(filename, update_cycle):
    """
    Return Timestamp of NOAA OFS filename based on naming convention.
    This is for OFS output with 1 timestep per file (everything but NYOFS)

    Parameters
    ----------
    filename : str
        Filename for which to decipher datetime.
    update_cycle : int
        Update cycle for COOPS OFS -- typically 6 but WCOFS is 24

    Returns
    -------
    Timestamp
        datetime of the time(s) in the file.

    Examples
    --------
    >>> fname = 'nos.cbofs.fields.n001.20220701.t00z.nc' #old format
    >>> file2dt(fname,6)
    Timestamp('2022-06-30 19:00:00')
    """

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
        dt -= update_cycle

    # construct datetime. dt might be negative.
    date += pd.Timedelta(f"{dt} hours")

    return date.to_pydatetime()


def prune_files_to_daterange(nc_list, fc_list, start, end, update_cycle):

    # keep nowcast/forecast files in time range
    pruned_nc_list = []
    pruned_fc_list = []
    pruned_dts = []
    dts = [file2dt(f.split("/")[-1], update_cycle) for f in nc_list]

    # ideally this buffer should be based on output timestep
    # -- but 3 hours is the least resolution offered so this works
    buffer = datetime.timedelta(hours=3)

    if start is None:
        start = min(dts)
    if end is None:
        end = max(dts) + datetime.timedelta(days=10)  # longest model forecast is 5 days

    for f, dt in zip(nc_list, dts):
        if (dt >= (start - buffer) and dt <= end + (buffer)):
            pruned_nc_list.append(f)
            pruned_dts.append(dt)

    # remove 0th nowcast if exists
    # pruned_nc_list = [f for f in pruned_nc_list if not fnmatch.fnmatch]

    pruned_nc_list = [x for y, x in sorted(zip(pruned_dts, pruned_nc_list))]

    # if the start date is wholly in the forecast range this will tank here (empty list)
    regex = re.compile(".t[0-9]{2}z.")
    try:
        last_nc_file = pruned_nc_list[-1].split("/")[-1]
        if file2dt(last_nc_file, update_cycle) < end:
            cycle = regex.findall(last_nc_file)[0][2:4]
            date = pd.to_datetime(last_nc_file, format="%Y%m%d", exact=False).strftime("%Y%m%d")
            for f in fc_list:
                if f.find(date + ".t" + cycle + "z") + f.find("t" + cycle + "z." + date) > -1:
                    pruned_fc_list.append(f)
            dts = [
                file2dt(f.split("/")[-1], update_cycle) for f in pruned_fc_list
            ]
            pruned_fc_list = [x for y, x in sorted(zip(dts, pruned_fc_list))]
    except IndexError:
        print("No nowcast files available")
        # no_nowcasts = True
        dts = [file2dt(f.split("/")[-1], update_cycle) for f in fc_list]
        sorted_fc_list = [x for y, x in sorted(zip(dts, fc_list))]
        cycle = regex.findall(sorted_fc_list[-1])[0][2:4]
        date = pd.to_datetime(sorted_fc_list[-1], format="%Y%m%d", exact=False).strftime("%Y%m%d")
        for f in sorted_fc_list:
            if f.find(date + ".t" + cycle + "z") + f.find("t" + cycle + "z." + date) > -1:
                pruned_fc_list.append(f)

    return pruned_nc_list + pruned_fc_list
