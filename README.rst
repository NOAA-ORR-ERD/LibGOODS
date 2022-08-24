libGOODS
========

Python package for retrieving environmental data needed for running GNOME model (shorelines, currents, winds)

**NOTE:**

LibGOODS is under active development -- its API will change.

Contributions are welcome, but we encourage you to work with the develop branch, and make sure to always pull the latest version before making any bug reports, comments or pull requests.

Installation
------------

This project relies on conda for installation and managing of the project dependencies.

1. `Download and install miniconda for your operating system <https://docs.conda.io/en/latest/miniconda.html>`_.

2.  Clone this repository with `git`.

3.  Once conda is available build the environment for this project with. Note: Below we use an
    environment name of ``libgoods`` but you can choose any environment name.

    .. code-block::

       conda env create --name libgoods -c conda-forge python=3.9
       conda activate libgoods

    The above command creates a new conda environment titled ``libgoods`` and installs Python 3.9 from
    conda-forge.

4. Install project dependencies

   .. code-block::

      conda install -c conda-forge --file conda_requirements.txt

5. Install test dependencies

   .. code-block::

      conda install -c conda-forge --file conda_requirements_test.txt

6. Install the local package for development:

   .. code-block::

      pip install -e .

6. Install ``model_catalogs``.

   Clone the repository at
   `https://github.com/NOAA-ORR-ERD/model_catalogs <https://github.com/NOAA-ORR-ERD/model_catalogs>`_
   and follow the instructions for installing the project. A summary of the steps:

   .. code-block::

      cd ../..
      git clone https://github.com/NOAA-ORR-ERD/model_catalogs/
      cd model_catalogs
      conda install -c conda-forge --file conda-requirements.txt
      pip install -r pip-requirements.txt
      pip install -e .

Command-Line Examples
---------------------

Usage
^^^^^

.. code-block::

   usage: fetch-model [-h] [-t {hindcast,nowcast,forecast}] [-s START] [-e END] [-f] [--bbox [BBOX]] [--surface] [-n STANDARD_NAMES]
                      [-o OUTPUT] [-l] [--show-bounds]
                      [model_name]

   Fetch model output.

   positional arguments:
     model_name            Name of the model

   optional arguments:
     -h, --help            show this help message and exit
     -t {hindcast,nowcast,forecast}, --timing {hindcast,nowcast,forecast}
                           Model Timing Choice.
     -s START, --start START
                           Request start time
     -e END, --end END     Request end time
     -f, --force           Overwrite existing files
     --bbox [BBOX]         Specify the bounding box
     --surface             Fetch only surface data.
     -n STANDARD_NAMES, --standard-names STANDARD_NAMES
                           Comma-delimited list of standard names to filter.
     -o OUTPUT, --output OUTPUT
     -l, --list-models     Print the available models and exit.
     --show-bounds         Show the bounds of the model and exit.

Examples
--------

The following example downloads HYCOM, subsets the data to a bounded region by 0° Longitude, 0°
Latitude, and 10° Longitude, 10° Latitude for the dates below.

.. code-block::

   fetch-model HYCOM --surface --bbox 0,0,10,10 -t forecast -s 2022-08-15 -e 2022-08-16


By default the fetch-model command line interface will download to a new folder called output
wherever the command is invoked. Clients can specify an output directory or the output filename
explicitly with the ``-o`` argument.


The following example lists all the models available to the interface.


.. code-block::

   fetch-model -l


The following example displays the model's bounding box:

.. code-block::

   fetch-model LEOFS --show-bounds
