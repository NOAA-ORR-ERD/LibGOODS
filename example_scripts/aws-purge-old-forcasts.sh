#!/bin/bash

NOWCAST_SIZE=`find -E /Volumes/Fury\ 2/s3 -regex '.*.n[0-9]{3}.*' -exec stat -q -f "%z" %s {} + | awk '{s+=$1} END {print s}'`
FORECAST_SIZE=`find -E /Volumes/Fury\ 2/s3 -regex '.*.f[0-9]{3}.*' -exec stat -q -f "%z" %s {} + | awk '{s+=$1} END {print s}'`

echo 'NOWCAST TOTAL SIZE:' $(($NOWCAST_SIZE / 1024 / 1024 / 1024))'gb'
echo 'FORECAST TOTAL SIZE:' $(($FORECAST_SIZE / 1024 / 1024 / 1024))'gb'

# remove forecast files older than a day
find -E /Volumes/Fury\ 2/s3 -regex '.*.f[0-9]{3}.*' -mtime +1d -exec rm {} \;

FORECAST_SIZE=`find -E /Volumes/Fury\ 2/s3 -regex '.*.f[0-9]{3}.*' -exec stat -q -f "%z" %s {} + | awk '{s+=$1} END {print s}'`
echo 'FORECAST TOTAL SIZE AFTER CLEANUP:' $(($FORECAST_SIZE / 1024 / 1024 / 1024))'gb'