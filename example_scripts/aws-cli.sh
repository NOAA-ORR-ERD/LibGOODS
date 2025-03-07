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

# get now cast data
AWS_CONFIG_FILE="./example_scripts/aws-cli-config" aws s3 sync s3://noaa-nos-ofs-pds/ /Volumes/Fury\ 2/s3 \
	--no-sign-request \
	--exclude "*" \
	--include "*wcofs/netcdf/$DATEPATTERN$TWODPATTERN" \
	--include "*sscofs/netcdf/$DATEPATTERN$THREEDPATTERN" \
	--include "*ngofs2/netcdf/$DATEPATTERN$TWODPATTERN" \
	--include "*cbofs/netcdf/$DATEPATTERN$THREEDPATTERN" \
	--include "*tbofs/netcdf/$DATEPATTERN$THREEDPATTERN" \
	--include "*dbofs/netcdf/$DATEPATTERN$THREEDPATTERN" \
	--include "*gomofs/netcdf/$DATEPATTERN$TWODPATTERN" \
	--include "*ciofs/netcdf/$DATEPATTERN$THREEDPATTERN" \
	--include "*sfbofs/netcdf/$DATEPATTERN$THREEDPATTERN" \
	--include "*leofs/netcdf/$DATEPATTERN$THREEDPATTERN" \
	--include "*lmhofs/netcdf/$DATEPATTERN$THREEDPATTERN" \
	--include "*loofs/netcdf/$DATEPATTERN$THREEDPATTERN" \
	--include "*lsofs/netcdf/$DATEPATTERN$THREEDPATTERN"

TWODPATTERN="*2ds$FORECAST*"      # forecast
THREEDPATTERN="*fields$FORECAST*" # forecast

# get forecast data for the specific day we care about
AWS_CONFIG_FILE="./aws-cli-config" aws s3 sync s3://noaa-nos-ofs-pds/ /Volumes/Fury\ 2/s3 \
	--no-sign-request \
	--exclude "*" \
	--include "*wcofs/netcdf/$DATEPATTERN$TWODPATTERN" \
	--include "*sscofs/netcdf/$DATEPATTERN$THREEDPATTERN" \
	--include "*ngofs2/netcdf/$DATEPATTERN$TWODPATTERN" \
	--include "*cbofs/netcdf/$DATEPATTERN$THREEDPATTERN" \
	--include "*tbofs/netcdf/$DATEPATTERN$THREEDPATTERN" \
	--include "*dbofs/netcdf/$DATEPATTERN$THREEDPATTERN" \
	--include "*gomofs/netcdf/$DATEPATTERN$TWODPATTERN" \
	--include "*ciofs/netcdf/$DATEPATTERN$THREEDPATTERN" \
	--include "*sfbofs/netcdf/$DATEPATTERN$THREEDPATTERN" \
	--include "*leofs/netcdf/$DATEPATTERN$THREEDPATTERN" \
	--include "*lmhofs/netcdf/$DATEPATTERN$THREEDPATTERN" \
	--include "*loofs/netcdf/$DATEPATTERN$THREEDPATTERN" \
	--include "*lsofs/netcdf/$DATEPATTERN$THREEDPATTERN"
