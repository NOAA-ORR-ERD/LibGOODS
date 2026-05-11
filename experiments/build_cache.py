#!/usr/bin/env python

"""
Python script to call the aws command line to sync the aws cache

Notes:

Currently hard-coded to only sync nowcast files from today
File type (fields or 2ds set to mirror what's in the libGOODS archive on servers)

"""

import datetime
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from libgoods.utilities import asdate

AWS_OFS_ENDPOINT = "s3://noaa-nos-ofs-pds/"

def set_cache_dir(cache_path=None):
    """
    Set the cache directory -- where the cache will go.

    The default Cache path is set, and it is returned, so you know what it was set to.

    If None:

    The path is set to the value of LIBGOODS_CACHE environment variable.

    If it doesn't exist, it is set to "./libgoods-cache"
    in the current working directory.


    Parameters
    ----------
    cache_path : PathLike
        The Path to where to store the cache.
        If a relative path, it will use the current working directory when
        this function is called.

    Returns
    -------
    type:
        pathlib.Path

    The cache path as set.
    """

    global CACHE_DIR

    if cache_path is None:
        # look for the Environment variable
        cache_path = os.getenv('LIBGOODS_CACHE')
        if cache_path is None:
            CACHE_DIR = Path() / "libgoods-cache"
        else:
            CACHE_DIR = Path(cache_path).resolve()
    else:
        CACHE_DIR = Path(cache_path).resolve()


    CACHE_DIR.mkdir(exist_ok=True)

    return CACHE_DIR

NUM_PARALLEL = 5

# AWS_COMMAND = []

def get_last_nowcast_date(model):
    """
    This will sync the forecast files -- going from
    now to forward.
    """
    # first see how far the nowcast files go
    model_dir = CACHE_DIR / model
    try:
        last_nowcast_file = sorted(model_dir.rglob("*n0??.nc"))[-1]
    except IndexError:
        return None
    year, month, day = (int(n) for n in str(last_nowcast_file).split("/")[-4:-1])
    last_nowcast_date = datetime.date(year,  month, day)

    return last_nowcast_date

def get_forecast_files(model):
    """
    This will sync the forecast files -- going from
    the last nowcast file forward 6? days
    now to forward.
    """
    # first see how far the nowcast files go
    model_dir = CACHE_DIR / model
    last_nowcast_file = sorted(model_dir.rglob("*n0??.nc"))[-1]
    year, month, day = (int(n) for n in str(last_nowcast_file).split("/")[-4:-1])
    last_nowcast_date = datetime.date(year,  month, day)

def build_aws_command(model, date, which_set, cast):
    """
    makes the file glob for a particular model, set, and cast
    """
    date_pattern = date.strftime("%Y/%m/%d/")
    file_path=f"{date_pattern}*{which_set}{cast}*"
    file_glob = f'*netcdf/{file_path}'
    # NOTE: you need to quote things with a * in them for the shell
    #       but not when passing directly to subprocess.call()
    command = ['aws',
               's3',
               'sync',
               f's3://noaa-nos-ofs-pds/{model}',
               f'{CACHE_DIR}/{model}',
               '--no-sign-request',
               '--size-only',
               '--exclude',
               '*',
               '--include',
               f'{file_glob}',
               ]

    return command

def purge_forecast_files():
    """
    Removes any forecast files before the lastest nowcast
    Loops through all models.
    """
    set_cache_dir()

    models = [p.stem for p in CACHE_DIR.iterdir() if p.is_dir()]

    for model in models:
        d = get_last_nowcast_date(model)
        print(d)
        for root, dirs, files in (CACHE_DIR / model / "netcdf").walk():
            print(f"Current Directory: {root}")
            if str(root).endswith(f"{d.year:04}/{d.month:02}/{d.day:02}"):
                print("it's the current one:")
                raise Exception
            for file in files:
                file_path = root / file
                # print(f"File: {file_path}")


def build_aws_sync_commands(MODEL, PATTERN, start_date, end_date):

    """
    Syncs the local cache with the OFS models on AWS

    Parameters
    ----------
    MODEL : str
        The model to download (in COOPS lower case)
    PATTERN : str
        Which "version" to get: either '2ds' or 'fields'
    days_back: int = 0
        How many days in the past to fetch. 0 is only today
        1 is yesterday and today, etc.
    Returns
    -------
    None:
      Waits to return until after the sync process is complete.

    """
    today = datetime.date.today()

    # nowcast files
    if end_date > today:
        dates = [today + datetime.timedelta(days=1)] # extra to make sure -- could be the next day in UTC
    else:
        dates = [end_date]
    while dates[-1] > start_date:
        dates.append(dates[-1] - datetime.timedelta(days=1))
    nowcast_commands = []
    for date in dates:
        nowcast_commands.append(build_aws_command(MODEL, date, PATTERN, ".n"))

    # forecast files
    if end_date >= today:
        # maybe some day, we can break this down
        forecast_commands = [build_aws_command(MODEL, end_date, PATTERN, ".f")]
    else:
        forecast_commands = []

    return nowcast_commands, forecast_commands



def run_command(command):
    print("Starting Up:", command)
    try:
        result = subprocess.run(command)
        return "aws sync command finished"
    except subprocess.CalledProcessError as e:
        return f"Command '{command}' failed with error: {e.stderr.decode()}"


def run_in_parallel(commands):
    """
    Run the multiple subprocess commands all at once

    Naomi reported that running ten at once was optimum -- who knows?

    Probably different on every machine and network state.

    Code adapted from Google ...
    """

    with ProcessPoolExecutor(max_workers=NUM_PARALLEL) as executor:
        # Map the function to the list of commands
        results = executor.map(run_command, commands)

    for result in results:
        print(result)


# Google's version --might want to borrow some of this.
# def run_command(command):
#     """Function to execute a command and return its completion status."""
#     try:
#         # subprocess.run is good for simple commands and blocks the worker process until completion
#         subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         return f"Command '{command}' finished successfully."
#     except subprocess.CalledProcessError as e:
#         return f"Command '{command}' failed with error: {e.stderr.decode()}"

    # # List of commands to run
    # commands = [
    #     'echo "hello from command 1" && sleep 1',
    #     'echo "hello from command 2" && sleep 2',
    #     'echo "hello from command 3" && sleep 1',
    #     'echo "hello from command 4" && sleep 3',
    #     'non_existing_command', # Example of a failing command
    # ]

# Set the number of parallel processes (e.g., number of CPU cores)



# There should be some way to get this list from libgoods.

ALL_MODELS = [
            'wcofs', 'sscofs', 'ngofs2', 'cbofs', 'tbofs', 'dbofs', 'gomofs',
            'ciofs', 'sfbofs', 'leofs', 'loofs', 'lmhofs', 'lsofs'
        ]

USAGE = ('You need to pass in the number of days back, and\n'
         'a list of models to cache, or "all" for all models.\n'
         f'Options are: {ALL_MODELS}\n'
         'Example:\n'
         'build_cache 3 cbofs')


def sync_nos_aws(models, start_date, end_date, num_parallel=NUM_PARALLEL):

    """
    Syncs the local cache with the OFS models on AWS

    Runs num_parallel commands in parallel


    Parameters
    ----------
    models : list of models to sync (in COOPS lower case)

    start_date: datetime.date
        when to start (how far back in the past)
        defaults to today

    end_date: datetime.date
        when to stop -- defaults to today

    num_parallel: int
        How many subprocesses to run in parallel (default is 5)

    Returns
    -------
    None:
        Processes are farmed out, and files should be created.
    """
    start_date = asdate(start_date)
    end_date = asdate(end_date)

    commands = []
    for model in models:
        if model in ['wcofs', 'ngofs2', 'gomofs']:
            pattern = '2ds'
        else:
            pattern = 'fields'
        forecast_comands, nowcast_commands = build_aws_sync_commands(
                                                model,
                                                pattern,
                                                start_date,
                                                end_date)
        commands.extend(nowcast_commands)
    # get the nowcast first
    run_in_parallel(commands)
    # and now the forecast (nowcast has to be run first, to know what's there.)
    run_in_parallel(forecast_commands)


if __name__ == "__main__":

    try:
        days_back = int(sys.argv[1])
        models = sys.argv[2:]
        if models[0] == "all":
            models = ALL_MODELS
    except IndexError:
        print(USAGE)
        sys.exit()

    set_cache_dir()

    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days_back)

    sync_nos_aws(models, start_date, end_date, num_parallel=NUM_PARALLEL)

    print("Syncing:", models)






