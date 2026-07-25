"""
Sample code for using libgoods itself to get a small subset for tests

kind of a recursive testing strategy, but it's something.

This one subsets NGOFS2

"""


import numpy as np
import xarray as xr

# m = api.get_model('NGOFS2')

# print(m.actual_start)

# print(m.actual_end)

# bounds = ((-89.5, 28.90), ( -89.35, 28.95)) # lower-left, upper-right

# subset = api.get_model_subset('NGOFS2',
#                               m.actual_end - timedelta(hours=12),
#                               m.actual_end,
#                               bounds,
#                               cross_dateline=False,
#                               environmental_parameters=['surface currents'])

# print("writing")

# subset.write_nc("small_fvcom_example.nc")


# m = api.get_model('GFS')

# print(m.actual_start)

# print(m.actual_end)

# bounds = ((-90, 27), ( -85, 30)) # lower-left, upper-right

# subset = api.get_model_subset('GFS',
#                               m.actual_end - timedelta(hours=12),
#                               m.actual_end,
#                               bounds,
#                               cross_dateline=False,
#                               environmental_parameters=['surface winds']
#                               )

# print("writing")

# subset.write_nc("small_gfs_example.nc")

# For GFS -- going directly to the source, so as to get all the variables.
gfs_url = "https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_0p25deg/Best"

# just an example -- off the bird's foot
bounds = ((-90, 27), ( -85, 30))

ds = xr.open_dataset(gfs_url)

ds['time'][-1]

end_time = ds['time'][-1] - np.timedelta64(24, 'h')
start_time = ds['time'][-1] - np.timedelta64(36, 'h')

# subset all the time coordinates
print(ds.nbytes)
ds2 = ds.sel(time=slice(start_time, end_time))
ds3 = ds2.sel(time1=slice(start_time, end_time))
ds4 = ds3.sel(time2=slice(start_time, end_time))
ds5 = ds4.sel(time3=slice(start_time, end_time))
print(ds5.nbytes)

# subset to the surface level
ds6 = ds5.xsg.subset_vertical_level(level=10, method='nearest')
print(ds6.nbytes)

# subset in space
# GFS lat monotonically decreasing
ds7 = ds6.sel(lat=slice(bounds[1][1], bounds[0][1]))
print(ds7.nbytes)
# GFS lon 0 -- 360
ds8 = ds7.sel(lon=slice(bounds[0][0] + 180, bounds[1][0] + 180))
print(ds8.nbytes)

vars_to_keep = {
    "Temperature_low_cloud_top_Mixed_intervals_Average", # to have a time3 var
    "Surface_Lifted_Index_surface", # time
    "Pressure_convective_cloud_top",# time1
    "Wind_speed_gust_surface", # time
    "u-component_of_wind_height_above_ground",
    "v-component_of_wind_height_above_ground"
    }


vars_to_drop = set([*ds8]) - vars_to_keep

ds9 = ds8.drop_vars(vars_to_drop)

# and write it out
ds9.to_netcdf('small_gfs_example.nc')





