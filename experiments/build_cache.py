#!/usr/bin/env python

"""
Python script to call the aws command line to sync the aws cache

Notes:
Currently hard-code to only sync nowcast files from today
File type (fields or 2ds set to mirror what's in the libGOODS archive on servers)

"""


import datetime
from pathlib import Path
import subprocess

AWS_OFS_ENDPOINT = "s3://noaa-nos-ofs-pds/"

CACHE_DIR = Path(__file__).parent / "libgoods-cache"
CACHE_DIR.mkdir(exist_ok=True)

AWS_COMMAND = []

def sync_model(MODEL, PATTERN='fields', date=None):

    date = datetime.datetime.now() if date is None else date

    PATTERN=PATTERN
    DATEPATTERN = date.strftime("%Y/%m/%d/")
    CAST=".n"

    FILE_PATH=f"{DATEPATTERN}*{PATTERN}{CAST}*"

    s3_url = f"s3://noaa-nos-ofs-pds/{MODEL}"

    FILE_GLOB = f'*netcdf/{FILE_PATH}'
    print("Using:", FILE_GLOB)
    # NOTE: you need to quite things with a * in them for the shell
    #       but not when passing directly to subprocess.call()
    command = ['aws',
               's3',
               'sync',
               f's3://noaa-nos-ofs-pds/{MODEL}',
               f'{CACHE_DIR}/{MODEL}',
               '--no-sign-request',
               '--size-only',
               '--exclude',
               '*',
               '--include',
               f'{FILE_GLOB}',
               ]

    print("Running:", command)
    subprocess.run(command)

if __name__ == "__main__":

    models = ['wcofs', 'sscofs', 'ngofs2', 'cbofs', 'tbofs', 'dbofs', \
              'gomofs', 'ciofs', 'sfbofs', 'leofs', 'loofs', 'lmhofs', 'lsofs']

    for model in models:
        print('Syncing', model)
        if model in ['wcofs', 'ngofs2', 'gomofs']:
            pattern = '2ds'
        else:
           pattern = 'fields'
        sync_model(MODEL=model, PATTERN=pattern)



