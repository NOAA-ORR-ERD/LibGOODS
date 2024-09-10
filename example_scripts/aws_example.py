import datetime
import os
from libgoods import coops_ofs_utils, model_em, utilities

model_id = 'WCOFS'
out_dir = 'wcofs'
model_type = 'FVCOM'

#to filter out only specific data variables of interest we need to provide standard_names used in model output attributes (or set to None to include all vars)
#snames_of_vars_to_include = ['eastward_sea_water_velocity','Northward_sea_water_velocity'] #NGOFS2
snames_of_vars_to_include = ['sea_water_x_velocity','sea_water_y_velocity','upward_sea_water_velocity'] #ROMS
#snames_of_vars_to_include = None #don't filter vars

start = datetime.datetime(2021,1,1,0,0)
end = datetime.datetime(2024,7,30,0,0)

#bbox = utilities.get_example_bbox(model_id)
bbox = (-123,44.3008,-122.93,47.3835) #mystery
#bbox = (-123.035,47.256,-121.755,48.411) #sos

fnames = coops_ofs_utils.get_aws_flist(model_id,start,end)
print(fnames)
    
#Download files from AWS
print('Downloading files from AWS')
filepaths = coops_ofs_utils.download_from_aws(fnames,out_dir=out_dir)

#Subset and write new smaller files 


# print('Subsetting and writing nc files')
newfiles = model_em.get_model_subset(filepaths,bounds=bbox,surface_index=0,out_dir=out_dir,snames_of_vars_to_include=snames_of_vars_to_include,drop_variables=['Itime','Itime2'],chunks={'time':1})

#This part does't work from script but do something like this to concatenate
#sometimes you have to do it in batches because the file list gets to long for the command line. I need to write a utility but I haven't yet.
"""
cd out_dir
fnames = [f.name for f in newfiles] 
cmd = 'ncra -Y ncrcat ' + ' '.join(fnames) + ' ' + model_id  + '2d.nc'
os.system(cmd)
"""

#ofn = model_em.concat(newfiles,model_id + '.nc')


