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
