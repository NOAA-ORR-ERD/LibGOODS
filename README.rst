libGOODS
========

Python package for retrieving environmental data needed for running GNOME model (shorelines, currents, winds)

**NOTE:**

LibGOODS is under active development -- its API will change.

Contributions are welcome, but we encourage you to work with the develop branch, and make sure to always pull the latest version before making any bug reports, comments or pull requests.

Installation
------------

This project relies on conda for installation and managing of the project dependencies.

It is tested with the packages from the conda-forge project:

https://conda-forge.org/

And works best with conda-forge packages

1. Download and install:
`miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ or
`miniforge <https://github.com/conda-forge/miniforge/releases>`_
for your operating system.

2. If you are using miniconda (or Anaconda), add the conda-forge channel to your configuration, and set `channel_priority` to strict::

  conda config --add channels conda-forge
  conda config --set channel_priority strict

3.  Clone this repository with `git`.

4.  Once conda is available build the environment for this project with.

    .. note:: Below we use an environment name of ``libgoods`` but you can choose any environment name.

    .. code-block::

       conda create --name libgoods python=3.13 --file conda_requirements.txt
       conda activate libgoods

    The above command creates a new conda environment titled ``libgoods`` with Python 3.13 and libgoods' dependencies


5. If you want to run the tests, you need the dependencies

   .. code-block::

      conda install --file conda_requirements_test.txt

6. Install the local package for development:

   .. code-block::

      pip install -e .



Examples
--------

libgoods is designed to be used in a Python scripting environment.


NOTE: let's put some examples in here, or ...

    .. The following example downloads HYCOM, subsets the data to a bounded region by 0° Longitude, 0°
    .. Latitude, and 10° Longitude, 10° Latitude for the dates below.

    .. .. code-block::

    ..    fetch-model HYCOM --surface --bbox 0,0,10,10 -t forecast -s 2022-08-15 -e 2022-08-16


    .. By default the fetch-model command line interface will download to a new folder called output
    .. wherever the command is invoked. Clients can specify an output directory or the output filename
    .. explicitly with the ``-o`` argument.


    .. The following example lists all the models available to the interface.


    .. .. code-block::

    ..    fetch-model -l


    .. The following example displays the model's bounding box:

    .. .. code-block::

    ..    fetch-model LEOFS --show-bounds
