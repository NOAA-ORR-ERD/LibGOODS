#script demonstrating use of xaray-subset-grid with TDS aggregations

from libgoods import models, utilities, coops_ofs
import datetime

model_id = 'WCOFS'
model_type = 'ROMS'  #this is the only model that has aggregations
fpath = coops_ofs.coops(model_id).get_ioos_tds_agg_url()
driver = 'opendap'

start = datetime.datetime.today()
end = start + datetime.timedelta(days=4)

#bounds = (-76.762,38.899,-75.997,39.352)
bounds = utilities.get_example_bbox(model_id)
   
if model_type == 'FVCOM': 
    m = models.fvcom()    
elif model_type == 'ROMS': 
    m = models.roms(tvar = 'time') #its aggregated on this new time variable    
else:
    raise NotImplementedError
    
m.open_ds(fpath,driver=driver)
m.subset_time(start,end)
m.select_surface()
m.filter_variables(variable_list = ['eastward_sea_water_velocity','northward_sea_water_velocity'])

##These last two steps hang (even w/o doing the subsetting first.
m.subset_grid(bounds)
m.write_nc(model_id + '.nc')
    