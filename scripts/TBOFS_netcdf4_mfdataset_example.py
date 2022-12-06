'''

'''

import model_catalogs as mc
import datetime
from libgoods import file_processing
import time

main_cat = mc.setup() #just using model_catalogs to get the url list
bounds = [-82.9, 27.3, -82.6, 27.7]
model_id = 'TBOFS'
model_source = 'coops-forecast-noagg'
cat = main_cat[model_id][model_source]    

start = datetime.datetime.today()
end = (start + datetime.timedelta(days=2))

mc.select_date_range(cat,start_date=start,end_date=end) #this could alternatively be done on the xarray ds

urls = cat.urlpath

t0 = time.time()

model = file_processing.roms()
var_map = {"time": "ocean_time"}
model.open_nc(urls)
model.get_dimensions(var_map=var_map)
model.subset(bounds)


ofn = 'tbofs_mf.nc'
model.write_nc(var_map=var_map, ofn=ofn)
   
    
t1 = time.time()
print('Elapsed time')
print((t1-t0)/60.0)