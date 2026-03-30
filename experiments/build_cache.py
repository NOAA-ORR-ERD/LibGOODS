#!/usr/bin/env python

"""
Python script to call the aws command line to sync the aws cache

Notes:

Currently hard-coded to only sync nowcast files from today
File type (fields or 2ds set to mirror what's in the libGOODS archive on servers)

"""

import datetime
from pathlib import Path
import subprocess
import sys

AWS_OFS_ENDPOINT = "s3://noaa-nos-ofs-pds/"

CACHE_DIR = Path(__file__).parent / "libgoods-cache"
CACHE_DIR.mkdir(exist_ok=True)

NUM_PARALLEL = 5

# AWS_COMMAND = []

def sync_model(MODEL, PATTERN='fields', days_back=0):

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
    dates = [today - (i * datetime.timedelta(days=1)) for i in range(days_back, -1,  -1)]

    s3_url = f"s3://noaa-nos-ofs-pds/{MODEL}"
    CAST=".n"

    commands = []
    for date in dates:
    #    PATTERN=PATTERN
        DATEPATTERN = date.strftime("%Y/%m/%d/")
        FILE_PATH=f"{DATEPATTERN}*{PATTERN}{CAST}*"


        FILE_GLOB = f'*netcdf/{FILE_PATH}'
        print("Using:", FILE_GLOB)
        # NOTE: you need to quote things with a * in them for the shell
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
        command.append(command)
    return command


def run_command(command):
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

    with ProcessPoolExecutor(max_workers=NUM_PARALLEL) as executor:
        # Map the function to the list of commands
        results = executor.map(run_command, commands)

    for result in results:
        print(result)


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



if __name__ == "__main__":

    try:
        days_back = int(sys.argv[1])
        models = sys.argv[2:]
        if models[0] == "all":
            models = ALL_MODELS
    except IndexError:
        print(USAGE)
        sys.exit()

    print("Syncing:", models)

    commands = []

    for model in models:
        print('Syncing', model)
        if model in ['wcofs', 'ngofs2', 'gomofs']:
            pattern = '2ds'
        else:
           pattern = 'fields'
        commands.extend(build_aws_sync_commands(MODEL=model, PATTERN=pattern, days_back=days_back))





