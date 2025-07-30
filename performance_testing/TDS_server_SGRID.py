"""
example of hitting a TDS server for a structured grid

To be used for experimenting with performance.

"""
from datetime import datetime
from libgoods.api import models

from timer import Timer

start = "2025-06-23T00:00"
end = "2025-07-23T00:00"

wpac = models.WPAC()

# change this if you want (right now its set to {'time':1} by default which is not good)
wpac.chunks = {'s_rho':1}

t = Timer()
wpac.open_ds()
t("opening the dataset")


# make it smaller in various ways
wpac.select_surface()
t("selecting the surface")


wpac.subset_time(start, end)
t("subsetting in time")

wpac.subset_grid((117.3, 21.2, 124.5, 25.8))
t("subsetting grid")

wpac.filter_variables()
t("filtering_variables")

# wpac = wpac.compute()
# t("computing the whole thing")

#write it
wpac.write_nc('wpac.nc')
t("saving as netCDF")

t.end()


