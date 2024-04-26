import datetime
from libgoods import metadata, model_em, utilities, coops_ofs_utils

model_id = 'CBOFS'
start = datetime.datetime(2024,4,1,0,0)
end = datetime.datetime(2024,4,4,0,0)
bbox = (-77.02,37.85,-75.5,39.617)

#meta = metadata.get_metadata_for_model(model_id,'ioos-forecast-agg')
#url = meta['sources'][0]['args']['urlpath']

flist = coops_ofs_utils.get_tds_flist(model_id,start,end)
#to filter out only specific data variables of interest we need to provide standard_names used in model output attributes (or set to None to include all vars)
snames_of_vars_to_include = ['sea_water_x_velocity','sea_water_y_velocity','surface_eastward_wind','surface_northward_wind']




#Subset and write file
out_dir = 'cbofs'


print('Subsetting and writing nc files')
ofn = model_em.get_model_subset(flist,start=None,end=None,bounds=bbox,surface_index=-1,out_dir=out_dir,snames_of_vars_to_include=snames_of_vars_to_include,tvar_name='ocean_time',check_exists=False)

cmd = 'ncra -Y ncrcat ' + ' '.join(ofn) + ' ' + model_id  + '.nc'
os.system(cmd)



