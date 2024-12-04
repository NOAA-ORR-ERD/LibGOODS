#script demonstrating use of xaray-subset-grid with s3/zarr aggregations


from libgoods import models, utilities, coops_ofs
from pathlib import Path
import datetime
model_dict  = {'SSCOFS':models.fvcom()}

model_id = 'SSCOFS'

fpath = coops_ofs.coops(model_id).get_zarr_url()
driver = 'zarr'

start = datetime.datetime.today()
end = start + datetime.timedelta(days=4)

#bounds = (-76.762,38.899,-75.997,39.352)
bounds = utilities.get_example_bbox(model_id)

m = model_dict[model_id]  
    
m.open_ds(fpath,driver=driver)
m.subset_time(start,end)
m.select_surface()
m.filter_variables()
m.subset_grid(bounds)
m.write_nc(model_id + '.nc')
    