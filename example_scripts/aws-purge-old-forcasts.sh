#!/bin/bash

unamestr=$(uname)
if [[ "$unamestr" == 'Darwin' ]]; then
	find="/usr/local/opt/findutils/libexec/gnubin/find"
else
	find=$(which find)
fi

FORECAST_SIZE=$($find /Volumes/Fury\ 2/s3 -regextype posix-extended -regex '.*.f[0-9]{3}.*' -exec stat -q -f "%z" %s {} + | awk '{s+=$1} END {print s}')

echo 'FORECAST SIZE BEFORE:' $(($FORECAST_SIZE / 1024 / 1024 / 1024))'gb'

# remove forecast files older than a day
$find /Volumes/Fury\ 2/s3 -regextype posix-extended -regex '.*.f[0-9]{3}.*' -mtime +1 -exec rm {} \;

FORECAST_SIZE=$($find /Volumes/Fury\ 2/s3 -regextype posix-extended -regex '.*.f[0-9]{3}.*' -exec stat -q -f "%z" %s {} + | awk '{s+=$1} END {print s}')
echo 'FORECAST TOTAL SIZE AFTER CLEANUP:' $(($FORECAST_SIZE / 1024 / 1024 / 1024))'gb'
