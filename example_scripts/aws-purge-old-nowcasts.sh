#!/bin/bash

unamestr=$(uname)
if [[ "$unamestr" == 'Darwin' ]]; then
	find="/usr/local/opt/findutils/libexec/gnubin/find"
else
	find=$(which find)
fi

NOWCAST_SIZE=$($find /Volumes/Fury\ 2/s3 -regextype posix-extended -regex '.*.n[0-9]{3}.*' -exec stat -q -f "%z" %s {} + | awk '{s+=$1} END {print s}')
echo 'NOWCAST SIZE BEFORE:' $(($NOWCAST_SIZE / 1024 / 1024 / 1024))'gb'

# remove forecast files older than a day
$find /Volumes/Fury\ 2/s3 -regextype posix-extended -regex '.*.n[0-9]{3}.*' -mtime +14 -exec rm {} \;

NOWCAST_SIZE=$($find /Volumes/Fury\ 2/s3 -regextype posix-extended -regex '.*.n[0-9]{3}.*' -exec stat -q -f "%z" %s {} + | awk '{s+=$1} END {print s}')
echo 'NOWCAST SIZE AFTER:' $(($NOWCAST_SIZE / 1024 / 1024 / 1024))'gb'
