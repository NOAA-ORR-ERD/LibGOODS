#!/bin/bash
#----------------------------------------
# Run LibGOODS demo
# 
# This script will use the fetch-data.py script to download Lake Ontario Operational Forcast System
# model output from 6 days ago to 2 days ago. The output will then be used as the forcing file for a
# GNOME oil spill simulation in the simple_script.py
#----------------------------------------
set -e

# Hack to activate conda in bash script
eval "$(command conda 'shell.bash' 'hook' 2> /dev/null)"

# Create output directory if it doesn't exist
[[ ! -d output ]] && mkdir output

checks() {
    # Check the conda environment to ensure that the conda environments exist
    set +e
    conda env list | grep model_catalogs
    if [[ $? -ne 0 ]]; then
        echo "Error: model_catalogs conda environment not defined. Please install the model_catalogs conda environment."
        exit 1
    fi
    conda env list | grep gnome
    if [[ $? -ne 0 ]]; then
        echo "Error: gnome conda environment not defined. Please install the gnome conda environment."
        exit 1
    fi
    set -e
}

fetch-data() {
    START_DATE=$(date -d '-6 days' '+%Y-%m-%d')
    END_DATE=$(date -d '-2 days' '+%Y-%m-%d')

    # Activate model_catalog and download forcing data
    echo "Activating goods38"
    conda activate goods38
    echo "fetching data"
    python fetch-data.py "$START_DATE" "$END_DATE" output
    echo "Deactivating conda environment"
    conda deactivate
}

run-scenario() {
    FORCING_FILE=$(ls -t output/*.nc | head -n1)

    # Activate PyGnome environment and run demo using data downloaded
    echo "Activating gnome environment."
    conda activate gnome
    echo "Running simulation"
    python simple_script.py "$FORCING_FILE"
    echo "Deactivating environment."
    conda deactivate
}


checks
fetch-data
run-scenario
