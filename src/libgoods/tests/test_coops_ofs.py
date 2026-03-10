"""
Tests  for the libgoods.coops_ofs package
"""

import datetime
import fnmatch
import re

import numpy as np
import pytest
import requests

from libgoods import coops_ofs

from .test_utilities import utc_now

# check if the TDS server is working:
TDS_URL = "https://opendap.co-ops.nos.noaa.gov/thredds/catalog/catalog.html"

try:
    r = requests.get(TDS_URL, timeout=5)
except (requests.ConnectionError, requests.ReadTimeout):
    SKIP_TDS = True
else:
    SKIP_TDS = False if r.status_code == 200 else True


# An example to test with:
# model_id = "LMHOFS"
model_id = "WCOFS"

# def test_metadata():
#     """
#     not really important, but what the heck ...
#     """
#     print(coops_ofs.OFS_INFO)

#     assert coops_ofs.OFS_INFO["WCOFS"].update_cycle == 24
#     assert coops_ofs.OFS_INFO["SSCOFS"].update_cycle == 6


# def test_file2dt():
#     pass
#     # how do i use the flist generated in test_tds_past_filelist?
@pytest.mark.skipif(SKIP_TDS, reason="COOPS TDS not responding")
def test_tds_past_filelist():
    """
    check if getting a file list entirely from the past works
    """

    dt = datetime.timedelta(days=10)
    start = utc_now() - dt
    end = start + datetime.timedelta(days=2)

    print(f"trying to get: {start} to {end}")

    flist = coops_ofs.get_tds_flist(model_id, start, end, file_type="fields")
    contains_fcs = any([fnmatch.fnmatch(f, "*.f???.*") for f in flist])

    for f in flist:
        print(f)

    assert contains_fcs is False, "File list contains forecasts"


def test_aws_future_filelist():
    """
    If you ask for the future, you should only get forecast files,
    and no nowcast files

    """
    dt = datetime.timedelta(days=1)
    start = utc_now() + dt
    utc_now()
    end = start + datetime.timedelta(days=2)

    flist = coops_ofs.get_aws_flist(model_id, start, end, file_type="fields")

    contains_fcs = any([fnmatch.fnmatch(f, "*.f???.*") for f in flist])
    contains_ncs = any([fnmatch.fnmatch(f, "*.n???.*") for f in flist])

    assert contains_fcs, "File list has no forecast files"
    assert contains_ncs is False, "File list contains nowcasts"


@pytest.mark.skipif(SKIP_TDS, reason="COOPS TDS not responding")
def test_tds_nc_fc_filelist():
    dt = datetime.timedelta(days=1)
    start = utc_now() - dt
    end = start + datetime.timedelta(days=3)

    flist = coops_ofs.get_tds_flist(model_id, start, end, file_type="fields")

    nc_last = np.where([fnmatch.fnmatch(f, "*.n[0-9]??.*") for f in flist])[0][-1]
    fcs = np.where([fnmatch.fnmatch(f, "*.f[0-9]??.*") for f in flist])[0]

    regex = re.compile(r"\d{8}")
    date_nc = regex.findall(flist[nc_last])[0]
    date_fc = regex.findall(flist[fcs[-1]])[0]

    regex = re.compile(".t[0-9]{2}z.")
    cycle_nc = regex.findall(flist[nc_last])[0]
    cycle_fc = regex.findall(flist[fcs[-1]])[0]

    assert date_nc + cycle_nc == date_fc + cycle_fc, (
        "Appended forecast does not match last nowcast cycle"
    )  # noqa: E501
