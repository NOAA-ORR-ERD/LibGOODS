#!/bin/bash

# !!!! Requires aws cli to be installed and available in $PATH
# !!!! https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html

set -e
set -x

# YYYY/MM/DD
if [ -z "${DATEPATTERN+x}" ]; then
	DATEPATTERN="$(date +%Y/%m/%d)/"
else
	DATEPATTERN="$DATEPATTERN/"
fi

NOWCAST=".n"
FORECAST=".f"
TWODPATTERN="*2ds$NOWCAST*"      # nowcast
THREEDPATTERN="*fields$NOWCAST*" # nowcast

find /Volumes/Fury\ 2/s3 -type f -name '*$NOWCAST*' -print0 |
	du --human-readable --total --files0-from=-
