import os

import numpy as np
import requests
import xarray as xr

#!!!!!This script requires cfgrib installed in your environment

# main directory
# https://ftp.ocean.weather.gov/grids/operational/NCOM/regional/GRIB2/

grib_url = "https://ftp.ocean.weather.gov/grids/operational/NCOM/regional/GRIB2/ncom_alaska_2025073000.grb2"  # Replace with the actual URL
local_filename = "test.grib"

if not os.path.exists(local_filename):
    print('Downloading file...')
    response = requests.get(grib_url)
    response.raise_for_status()  # Raise an exception for bad status codes

    with open(local_filename, "wb") as f:
        f.write(response.content)

    print(f"GRIB file downloaded to {local_filename}")

ds = xr.open_dataset(local_filename, engine="cfgrib")

time_base = ds.variables['time']
time_step = ds.variables['step']
time =  time_base.values + time_step

longitude = ds.variables['longitude'].values[:] - 360.0
latitude = ds.variables['latitude'].values[:]

slat = 56.82
nlat = 58.85
wlon = -137.82
elon = -131.93
idx = np.where((longitude >= wlon) & (longitude <=elon))[0]
idy = np.where((latitude >= slat) & (latitude <=nlat))[0]

longitude = longitude[idx[0]:idx[-1]]
latitude = latitude[idy[0]:idy[-1]]
u = ds.variables['uoe']
v = ds.variables['von']
u_data = u.values[:,idy[0]:idy[-1],idx[0]:idx[-1]]
v_data = v.values[:,idy[0]:idy[-1],idx[0]:idx[-1]]


# Create the xarray Dataset
ds_out = xr.Dataset(
    data_vars={
        "u": (("time", "latitude", "longitude"), u_data, {"units": u.attrs['units']}),
        "v": (("time", "latitude", "longitude"), v_data, {"units": v.attrs['units']}),
    },
    coords={
        "time": time,
        "latitude": latitude,
        "longitude": longitude,
    },
    attrs={"description": "GNOME compatible dataset"},
)

ds.to_netcdf('near_juneau.nc')
