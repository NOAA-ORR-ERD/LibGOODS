import datetime
from libgoods import model_em

#gulf of maine
url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_GOM3_FORECAST.nc'

#mass bay  
#url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc'

#to filter out only specific data variables of interest we need to provide standard_names used in model output attributes (or set to None to include all vars)
snames_of_vars_to_include = ['eastward_sea_water_velocity','northward_sea_water_velocity']
model_type = 'FVCOM'

start = '2023-10-16'
end = '2023-10-17'
bbox = (-71.59,40.88,-68.45,42.52)


   
#Subset and write file
out_dir = '.'

print('Subsetting and writing nc files')
ofn = model_em.get_model_subset(url,start,end,bbox,model_type=model_type,surface_only=True,out_dir=out_dir,snames_of_vars_to_include=snames_of_vars_to_include)






