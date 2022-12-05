import model_catalogs as mc
import datetime
from libgoods import model_fetch
from dask.diagnostics import ProgressBar

main_cat = mc.setup()
bounds = [-82.9, 27.3, -82.6, 27.7]
model_id = 'TBOFS'
model_source = 'coops-forecast-noagg'
cat = main_cat[model_id][model_source]    

start = datetime.datetime.today()
end = start + datetime.timedelta(days=2)


mc.select_date_range(cat,start_date=start,end_date=end) #this could alternatively be done on the xarray ds

print('to dask')
with ProgressBar():
 ds = cat.to_dask()

print('subsetting')
ds = model_fetch.select_surface(ds)
ds_ss = ds.em.filter(["eastward_sea_water_velocity", "northward_sea_water_velocity"])
ds_ss = ds_ss.em.sub_grid(bbox=bounds)

print('preparing')
delayed = ds_ss.to_netcdf('test.nc',compute=False)

print('writing')
with ProgressBar():
 result = delayed.compute()

