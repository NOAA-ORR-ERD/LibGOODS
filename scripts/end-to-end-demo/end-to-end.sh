#!/bin/bash
# Run LibGOODS demo
set -e

# Hack to activate conda in bash script
eval "$(command conda 'shell.bash' 'hook' 2> /dev/null)"

# Activate model_catalog and download forcing data
echo "Creating forcing file"
conda activate model_catalogs
python fetch-data.py 2022-5-3 2022-5-4 .
conda deactivate

# Activate PyGnome environment and run demo using data downloaded
echo "Running simulation"
conda activate gnome
python simple_script.py
conda deactivate
