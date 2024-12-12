'''

Once the xarray dataset is in memory, we call to_netcdf
'''

import model_catalogs as mc
import datetime
from libgoods import model_fetch
import xarray as xr
import time

main_cat = mc.setup()
bounds = [-82.9, 27.3, -82.6, 27.7]
model_id = 'TBOFS'
model_source = 'coops-forecast-noagg'
cat = main_cat[model_id][model_source]    

start = datetime.datetime.today()
end = start + datetime.timedelta(days=2)


mc.select_date_range(cat,start_date=start,end_date=end) #this could alternatively be done on the xarray ds

urls = cat.urlpath

t0 = time.time()
count = 0
for url in urls:
    print(count, "of ", len(urls))
    ds = xr.open_dataset(url)

    # print('to dask')
    # with ProgressBar():
     # ds = cat.to_dask()

    #print('subsetting')
    ds_ss = ds.em.filter(["sea_water_y_velocity","sea_water_x_velocity"])
    ds_ss = ds_ss.em.sub_grid(bbox=bounds)
    ds_ss = model_fetch.select_surface(ds_ss)
    
    ofn = 'tbofs' + str(count).zfill(3) +'.nc'
    ds_ss.to_netcdf(ofn)

    # print('preparing')
    # delayed = ds_ss.to_netcdf('test.nc',compute=False)

    # print('writing')
    # with ProgressBar():
     # result = delayed.compute()
    
    count = count+1
t1 = time.time()
print('Elapsed time')
print((t1-t0)/60)