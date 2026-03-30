"""
A test to see what's up with xarray losing CF coordinates...

Amy found this odd big ...

"""

from datetime import timedelta

import xarray as xr

from libgoods import models


bounds = (-76, 34, -75, 35)

e = models.ESPC()

print("opening dataset")
e.open_ds()

print(e.when())

end = e.actual_end
start = end - timedelta(days=1)

print(f"{e.ds.cf.coordinates=}")

e.subset_time(start, end)

e.subset_grid(bounds)

print(e.ds.cf.coordinates)

e.select_surface()

print(e.ds.cf.coordinates)

# hmm -- still has depth coordinate.

e.filter_variables()

print(e.ds.cf.coordinates)


print(e.size())

e.ds.to_netcdf('espc_out_raw.nc')
e.write_nc('espc_out.nc')

new_ds = xr.open_dataset('espc_out.nc')

print(new_ds.cf.coordinates)




