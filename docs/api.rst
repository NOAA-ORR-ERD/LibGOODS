``libgoods`` API
################

The libgoods package provides an API for top-level use.
This API should provide an interface to access core data directly.

Delving into the rest of the package should only be necessary if you
need to customize data access.

Finding models
==============

.. code-block:: python

    In [8]: from libgoods import api

    In [9]: models = api.list_model_names()

    In [10]:   for m in models:
        ...:       print(m)
        ...:
    LEOFS: Lake Erie -- NOAA/NOS Lake Erie Operational Forecast System
    LMHOFS: Lakes Michigan and Huron -- NOAA/NOS Lake Michigan and Huron Operational Forecast System
    LOOFS: Lake Ontario -- NOAA/NOS Lake Ontario Operational Forecast System
    LSOFS: Lake Superior -- NOAA/NOS Lake Superior Operational Forecast System
    NGOFS2: Northern Gulf of America -- NOAA/NOS Northern Gulf of America Operational Forecast System
    SSCOFS: Salish Sea and Columbia River -- NOAA/NOS Salish Sea and Columbia River Operational Forecast System
    CBOFS: Chesapeake Bay -- NOAA/NOS Chesapeake Bay Operational Forecast System
    CIOFS: Cook Inlet -- NOAA/NOS Cook Inlet Operational Forecast System
    DBOFS: Delaware Bay -- NOAA/NOS Delaware Bay Operational Forecast System
    GOMOFS: Gulf of Maine -- NOAA/NOS Northern Gulf of Maine Operational Forecast System
    TBOFS: Tampa Bay -- NOAA/NOS Tampa Bay Operational Forecast System
    WCOFS: US West Coast -- NOAA/NOS NWest Coast Operational Forecast System
    DOPPIO: Mid-Atlantic Bight and Gulf of Maine (Rutgers) --
    ESPC: Navy Earth System Prediction Capability -- Global Navy Earth System Prediction Capability
    HFRadar:  --
    NECOFS: Northeast Coastal Ocean Forecast (GOM7) --
    BostonHarbor: Boston Harbor, MA --
    Hampton: Hampton, NH --
    MassCoastal: Massachusetts Coastal Model --
    Scituate: Scituate, MA --
    HIIG: Hawaiian Islands 4 km --
    HIOEKG: Kaneohe Bay --
    HIOG: Oahu 1 km --
    HIOMSAG: Waikiki --
    HIOMSG: Oahu South Shore --
    MARIG: Guam and Northern Mariana Islands --
    SAMOA: Samoa --
    WPAC: Western North Pacific --
    TAMU: Texas/Louisiana Shelf Model -- Texas A&M / Texas General Land Office Shelf Model
    TBCOM:  --
    WFCOM: West Florida Coastal Ocean Circulation Model --
    GFS: Global Winds (GFS-1/4 degree) -- NOAA/NCEP Global Forecast System (GFS), 1/4 degree horizontal resolution

See: :py:mod:`libgoods.api` for the full specification.


