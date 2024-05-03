import datetime
import os
from libgoods import coops_ofs_utils, model_em, utilities

model_id = 'SSCOFS'
out_dir = 'sscofs'
model_type = 'FVCOM'

#to filter out only specific data variables of interest we need to provide standard_names used in model output attributes (or set to None to include all vars)
#snames_of_vars_to_include = ['eastward_sea_water_velocity','Northward_sea_water_velocity'] #NGOFS2
#snames_of_vars_to_include = ['sea_water_x_velocity','sea_water_y_velocity','upward_sea_water_velocity'] #ROMS
#snames_of_vars_to_include = None #don't filter vars

start = datetime.datetime(2024,4,19,0,0)
end = datetime.datetime(2024,4,21,0,0)

bbox = utilities.get_example_bbox(model_id)
#bbox = (-77.02,37.85,-75.5,39.617)

fnames = coops_ofs_utils.get_aws_flist(model_id,start,end)
    
#Download files from AWS
print('Downloading files from AWS')
filepaths = coops_ofs_utils.download_from_aws(fnames,out_dir=out_dir)

#Subset and write new smaller files 


# print('Subsetting and writing nc files')
newfiles = model_em.get_model_subset(filepaths,bounds=bbox,model_type=model_type,surface_only=True,out_dir=out_dir,snames_of_vars_to_include=snames_of_vars_to_include)

cmd = 'ncra -Y ncrcat ' + ' '.join(newfiles) + ' ' + model_id  + '.nc'
os.system(cmd)

#ofn = model_em.concat(newfiles,model_id + '.nc')


