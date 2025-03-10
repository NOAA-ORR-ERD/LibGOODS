#!/bin/bash

# !!!! Requires aws cli to be installed and available in $PATH
# !!!! https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html

set -e
set -x

CONFIG="/Volumes/Fury 2/libgoods/example_scripts/aws-cli-config"

if [ -z "${MODEL+x}" ]; then
	MODEL="cbofs"
fi

if [ -z "${PATTERN+x}" ]; then
	PATTERN="fields"
fi

if [ -z "${CAST+x}" ]; then
	CAST=".n"
fi

# YYYY/MM/DD
if [ -z "${DATEPATTERN+x}" ]; then
	DATEPATTERN="$(date +%Y/%m/%d)/"
else
	DATEPATTERN="$DATEPATTERN/"
fi

FILE_PATH="$DATEPATTERN*$PATTERN$CAST*"

AWS_CONFIG_FILE="$CONFIG" aws s3 sync s3://noaa-nos-ofs-pds/$MODEL /Volumes/Fury\ 2/s3/$MODEL \
	--no-sign-request \
	--size-only \
	--exclude "*" \
	--include "*/netcdf/$FILE_PATH"
