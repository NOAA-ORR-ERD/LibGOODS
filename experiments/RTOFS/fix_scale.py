import sys
import netCDF4
import shutil
import numpy as np

infile = sys.argv[1]
newfile = infile[:-3] + "_offset_fixed.nc"
shutil.copy(infile, newfile)

with netCDF4.Dataset(newfile, mode='a') as ds:

    for varname in ('water_u', 'water_v'):
    # for varname in ('water_u', ):
        var = ds.variables[varname]
        print("before:")
        print(repr(var.getncattr("add_offset")))
        print(repr(var.getncattr("scale_factor")))

        add_offset = var.getncattr("add_offset")
        if type(add_offset) == str:
            add_offset = float(add_offset.rstrip('f'))
        var.setncattr("add_offset", np.float32(add_offset))

        print("after:")
        print(repr(var.getncattr("add_offset")))
        print(repr(var.getncattr("scale_factor")))

