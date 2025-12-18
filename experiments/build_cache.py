#!/usr/bin/env python

import datetime
from pathlib import Path
import subprocess

AWS_OFS_ENDPOINT = "s3://noaa-nos-ofs-pds/"

CACHE_DIR = Path(__file__).parent / "libgoods-cache"
CACHE_DIR.mkdir(exist_ok=True)

AWS_COMMAND = []

def sync_model(MODEL, date=None, how_far_back=None):

    date = datetime.datetime.now() if date is None else date

    PATTERN="fields"
    DATEPATTERN = date.strftime("%Y/%m/%d")
    CAST=".n"

    FILE_PATH=f"{DATEPATTERN}*{PATTERN}{CAST}*"

    s3_url = f"s3://noaa-nos-ofs-pds/{MODEL}"

    command = ["aws", "s3", "sync",
               f"s3://noaa-nos-ofs-pds/{MODEL}",
               f"{CACHE_DIR}{MODEL}",
               "--no-sign-request",
               "--size-only",
               '--exclude', '"*"',
               '--include',
               f'"*netcdf/{FILE_PATH}"',
               ]
    print(command)
    subprocess.run(command)

if __name__ == "__main__":
    sync_model('cbofs')





