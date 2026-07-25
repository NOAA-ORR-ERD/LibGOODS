This is some code for figuring out what to do with RTOFS.

There are two problems:

1) It doesn't have the metadata for xarray_subset_grid to recognize it.
   There is some code in here to try to add it, but ...

   (note: There's a PR on xarray_subset_grid that should let it read these directly, but it needs some review before merging.)

2) The velocities are stored with a "scale" and "offset" - -but the offset is stored as a string, i.e. "0.0f" rather than a number, which makes xarray and netCDF4 barf on it.

There's code here to fix that with netCDF4, but that requires that you have a nc file first.

So what should work, but I haven't tried yet is:

- Open the Dataset with a flag so it won't try to decode the scale and offset.

- Subset it.

- Save it out as a netcdf file

- Use netCDF4 to fix the file.

Meanwhile, we should let Kelly or whoever, know that there's a bug in the TDS config.


