import datetime
from libgoods import metadata, model_em,utilities

model_id = 'CBOFS'
url = metadata.get_url(model_id,'ioos-forecast-agg')

#to filter out only specific data variables of interest we need to provide standard_names used in model output attributes (or set to None to include all vars)
snames_of_vars_to_include = ['sea_water_x_velocity','sea_water_y_velocity']
model_type = 'ROMS'

start = datetime.datetime.today()
end = start + datetime.timedelta(days=2)
bbox = utilities.get_example_bbox(model_id)

#Subset and write file
out_dir = 'output'

print('Subsetting and writing nc files')
ofn = model_em.get_model_subset(url,start,end,bbox,model_type=model_type,surface_only=True,out_dir=out_dir,snames_of_vars_to_include=snames_of_vars_to_include)






