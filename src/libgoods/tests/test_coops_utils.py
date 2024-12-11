"""
Tests  for the libgoods.coops_ofs package
"""
from netCDF4 import MFDataset, Dataset, num2date
from libgoods import coops_ofs
import pytest
import datetime
import fnmatch
import numpy as np
import re
import pandas as pd

model_id = 'LMHOFS'

def test_file2dt():
    pass
    #how do i use the flist generated in test_tds_past_filelist?

    
def test_tds_past_filelist():
    dt = datetime.timedelta(days=10)
    start = datetime.datetime.today()  - dt
    end = start + datetime.timedelta(days=2)
    m = coops_ofs.coops(model_id)
    flist = m.get_tds_flist(start,end,file_type='fields')
    contains_fcs = any([fnmatch.fnmatch(f, "*.f???.*") for f in flist])
    assert contains_fcs is False, f"File list contains forecasts"
    
def test_aws_future_filelist():
    dt = datetime.timedelta(days=1)
    start = datetime.datetime.today() + dt
    end = start + datetime.timedelta(days=2)
    m = coops_ofs.coops(model_id)
    flist = m.get_aws_flist(start,end,file_type='fields')
    contains_fcs = any([fnmatch.fnmatch(f, "*.f???.*") for f in flist])
    contains_ncs = any([fnmatch.fnmatch(f, "*.n???.*") for f in flist])
    assert contains_fcs, f"File list has no forecast files"
    assert contains_ncs is False, f"File list contains nowcasts"

def test_tds_nc_fc_filelist():
    dt = datetime.timedelta(days=1)
    start = datetime.datetime.today()  - dt
    end = start + datetime.timedelta(days=3)
    m = coops_ofs.coops(model_id)
    flist = m.get_tds_flist(start,end,file_type='fields')
    nc_last = np.where([fnmatch.fnmatch(f, "*.n[0-9]??.*") for f in flist])[0][-1]
    fcs = np.where([fnmatch.fnmatch(f, "*.f[0-9]??.*") for f in flist])[0]
    
    regex = re.compile("\d{8}")
    date_nc = regex.findall(flist[nc_last])[0]
    date_fc = regex.findall(flist[fcs[-1]])[0]

    regex = re.compile(".t[0-9]{2}z.")
    cycle_nc = regex.findall(flist[nc_last])[0]
    cycle_fc = regex.findall(flist[fcs[-1]])[0]
    
    assert date_nc + cycle_nc == date_fc + cycle_fc, f"Appended forecast does not match last nowcast cycle"
    