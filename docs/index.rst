############
``LibGOODS``
############

The Library for the GNOME Online Oceanographic Data Server (LibGOODS) is
a python library (and some utilities) designed to provide access to various
oceanographic models and data sources in a form suitable for the
`General NOAA Operational Modeling Environment <https://response.restoration.noaa.gov/gnomesuite>`_

While built to support the GNOME Suite (and specifically `WebGNOME <https://gnome.orr.noaa.gov>`_), it generally supports data format standards (e.g. The CF metadata standard), so its results can be useful for many other applications.


Problem Statement
=================

For oil spill modeling, or particle tracking models in general, and many other modeling uses, data and model results are required that provide the environmental conditions for the problem at hand: Ocean Currents, Surface Winds, etc.

There are multiple sources for these data, and many operational and semi-operational models that can provide the needed drivers.
However, each source of data, and each operator, makes their results available in slightly different ways.
Despite much progress in data standards and protocols (e.g. CF Metadata Standard, OPeNDAP), each data source does things in a slightly different way.
In common data analysis use-cases, it's manageable to find the data you need, download it, and then do whatever tweaking you need to make it work for you. However, in the emergency response use-case, NOAA needs to quickly and easily access many different data sources without having time to custom manipulate each data source.

In addition to adjustments due to file formats, meta-data, or access protocols,
users often need just a subset of the available data: only a particular time period, or only a smaller region than that covered by the entire model, which can be on very large domains.

``libgoods`` seeks to address these issues by providing a single simple API for accessing a variety of data sets and operational models in a consistent way.


Installation
============

``libgoods`` is currently only available in source form, at:

https://github.com/NOAA-ORR-ERD/libgoods

Note that is developed on an internal NOAA system -- if the version on GitHub seems out of date, feel free to ping us via a GitHub Issue.

Once you have the source, it can be installed via the standard Python:

``python -m pip install .``

Developing ``libgoods``
-----------------------

If you want to work on the source code, we have provided a
`pixi <https://pixi.prefix.dev/>`_ setup for development::

``pixi shell``


Should get you everything to need to work on the code.


.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Documentation

   whats_new
   api
   api/libgoods

