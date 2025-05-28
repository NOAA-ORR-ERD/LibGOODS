import datetime
from libgoods import model_em,utilities

model_id = 'NECOFS'
model_type = 'FVCOM'
url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/models/fvcom/NECOFS/Forecasts/NECOFS_GOM7_FORECAST.nc'

start = datetime.datetime.today()
end = start + datetime.timedelta(days=4)

#bounds = (-76.762,38.899,-75.997,39.352)
bounds = utilities.get_example_bbox(model_id)


drop_variables = ['Itime', 'Itime2']
chunks={'time':1}
snames_of_vars_to_include = ['Eastward Water Velocity','Northward Water Velocity']

#Subset and write file
out_dir = 'output'

print('Subsetting and writing nc files')
ofn = model_em.get_model_subset(url,start=start,end=end,bounds=bounds,surface_index=0,out_dir=out_dir,snames_of_vars_to_include=snames_of_vars_to_include,drop_variables=drop_variables,chunks=chunks,check_exists=False)






