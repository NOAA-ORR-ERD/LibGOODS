A place to put example data files.

These should only be small files -- large ones should be auto-dowloaded when needed.

NOTE: use pooch for this?

Example of how to use libgoods itself to make a small example file.

NOTE: this only works if you want an example file for which there is alrady libgods support, of course :-)

To get a small FVCOM example:

```
In [6]: api.list_model_names()
Out[6]:
['LEOFS: Lake Erie -- NOAA/NOS Lake Erie Operational Forecast System',

...

 'NGOFS2: Northern Gulf of America -- NOAA/NOS Northern Gulf of America Operational Forecast System',
 'SFBOFS: San Francisco Bay -- NOAA/NOS San Francisco Bay Operational Forecast System',
 'SSCOFS: Salish Sea and Columbia River -- NOAA/NOS Salish Sea and Columbia River Operational Forecast System',
 'CBOFS: Chesapeake Bay -- NOAA/NOS Chesapeake Bay Operational Forecast System',
...

There's lots more, but ...

Get a small subset:

In [11]: m = api.get_model('NGOFS2')

In [12]: m.actual_start
Out[12]: datetime.datetime(2026, 5, 31, 9, 0)

In [13]: m.actual_end
Out[13]: datetime.datetime(2026, 7, 26, 15, 0)
In [6]: bounds = ((89.50, 28.85), ( -89.35, 28.95)) # lower-left, upper-right

subset = api.get_model_subset('NGOFS2', m.actual_end, m.actual_end - timedelta(hours=6), bounds, cross_dateline=False, environmental_parameters=['surface currents'])





