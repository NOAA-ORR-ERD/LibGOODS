Examples
========

This examples folder contains (or will contain) examples for finding, querying, and subsetting
model data from the NOAA Operational Forecast System(s).

Installation
------------

### Linux

For local testing on a Linux machine (Windows instructions to follow) I was able to install the
`model_catalogs` and `PyGnome` development environments within a single conda based environment.

1. Clone the PyGnome project
   ```
   git clone https://github.com/NOAA-ORR-ERD/PyGnome/
   ```

2. Clone this project
   ```
   git clone https://github.com/NOAA-ORR-ERD/LibGOODS/
   ```

3. Install the PyGnome environment. Follow the README in the project, but these steps were valid at
   the time of authoring this document:

   ```
   cd PyGnome
   conda create -n gnome --file conda_requirements.txt
   cd py_gnome
   python setup.py develop
   cd ../..
   ```

4. Now install dependencies for `model_catalogs` on the same environment:
   ```
   cd LibGOODS/model_catalogs
   conda env update -f environment.yml --name gnome
   pip install -e .
   ```

The conda environment with the name `gnome` should now contain all the necessary project
dependencies to run both `model_catalogs` and PyGnome.


### Windows

Windows instructions to follow at a later date, but following the above Linux instructions may work.


Running
-------

Each model example will contain two files:
- `fetch.py` - Download the data locally, can optionally support CLI arguments to change subset
  region and date/times.
- `run_scenario.py` - Initializes and runs a simple PyGnome simulation of an oil-spill centered in
  the subsetted region of the data.


### Examples
The following is an example running the CIOFS fetch script.
```
(gnome) LibGOODS $ python scripts/examples/ciofs/fetch.py -f
Setting up source catalog
"complete" model source files are not yet available. Run `model_catalogs.complete_source_catalog()` to create this directory.
        Source catalog generated in 367.2 ms
Generating catalog specific for CIOFS hindcast
        Specific catalog generated in 5317.4 ms
Getting xarray dataset for model data
        Created dask-based xarray dataset in 42243.2 ms
Subsetting data
        Subsetted dataset in 1548.3 ms
Writing netCDF data to scripts/examples/ciofs/output/CIOFS_hindcast_20220620-20220621.nc. This may take a long time, ~20-minutes per 24h period is an estmate.
        Wrote output to disk in 1562459.4 ms
Complete
```

The following is an example running the CIOFS `run_scenario.py` script.
```
(gnome) LibGOODS $ python scripts/examples/ciofs/run_scenario.py
.../code/PyGnome/py_gnome/gnome/__init__.py:61: UserWarning: ERROR: The adios_db package, version >= 1.0.0 needs to be installed: Only required to use the ADIOS Database JSON format for oil data.
  warnings.warn(msg)
Reading start time from model output
Scenario Parameters
        start_time: 2022-06-20 00:00:00
        duration: 16 hours
        Δt: 15 min
        BBOX: (-154.5, 58.0) (-151.0, 58.0)
        Spill Location: (-153.0, 59.0)
Adding Current Mover from model data
Adding spill
Adding renderer
Running scenario
...
```
