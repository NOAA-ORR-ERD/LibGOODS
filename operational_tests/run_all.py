#!/usr/bin/env python
"""
run all the various models, tests, etc.

Script to run all the testing scripts

python run_all.py
    run all the scripts, except the ones with known issues.

python run_all.py no_skip
    run all the scripts, skipping none

python run_all.py script_one script_two
    run the specified scripts.
"""

import sys
import datetime
from pathlib import Path
import subprocess

# need to have some logic here
TEST_CACHE = False

# the systems that should be tested

# ones that hit various online services
# e.g. OpenDap, etc
ONLINE = ['GFS', 'TAMU']

# the ones that require a local cache
# need to add sfbofs in once we support that
LOCAL_CACHE = ['wcofs', 'sscofs', 'ngofs2', 'cbofs', 'tbofs', 'dbofs', 'sfbofs',
               'gomofs', 'ciofs',  'leofs', 'loofs', 'lmhofs', 'lsofs']


HERE = Path(__file__).parent
def run_all():
    """
    Runs all the scripts, each in a subprocess

    Then reports success and failures to stdout, as well as to:

    script_results.txt

    :param to_skip: list of scripts to skip -- useful for known failures

    script returns number of failures as error code, so it can be used
    in a CI test run. (e.g. 0 error code means zero failed scripts)
    """
    scripts = []
    for model_id in ONLINE:
        script = HERE / f'{model_id}_op_test.py'
        if not script.is_file():
            print(f'**********\nNo script for: {model_id}')
            print(f"{script} is missing!!\n")
        else:
            scripts.append(script)

    scripts = {p.relative_to(Path.cwd())
               for p in scripts}

    print(f"{len(scripts)} total scripts")

    for p in scripts:
        print(f"Running: {repr(p)}")

    successes = []
    failures = []

    for script in scripts:
        print("**************************")
        print("*")
        print("*  Running:   %s"%script)
        print("*")
        print("**************************")

        try:
            subprocess.check_call(["python", script], shell=False)
            successes.append(script)
        except subprocess.CalledProcessError:
            failures.append(script)

    with open("script_results.txt", 'w', encoding='utf-8') as outfile:
        outfile.write("libgoods Script Runner Report\n")
        outfile.write(f"Produced: {datetime.datetime.now()}\n")

        outfile.write("\nScripts that ran without Errors:\n")
        outfile.write("--------------------------------\n\n")
        outfile.writelines(f"{script}\n" for script in successes)

        outfile.write("\nScripts that Errored out:\n")
        outfile.write("-------------------------\n\n")
        outfile.writelines(f"{script}\n" for script in failures)

    return successes, failures


if __name__ == "__main__":
    print(sys.argv)

    successes, failures = run_all()

    print("Successful scripts:")

    for s in successes:
        print(s)

    print("Scripts with Errors:")

    for s in failures:
        print(s)

    sys.exit(len(failures))
