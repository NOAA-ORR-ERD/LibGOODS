import model_catalogs as mc
import datetime
import os
from libgoods import aws, model_em, utilities

model_id = 'LMHOFS'
out_dir = 'lmhofs'
model_type = 'FVCOM'

#to filter out only specific data variables of interest we need to provide standard_names used in model output attributes (or set to None to include all vars)
#snames_of_vars_to_include = ['eastward_sea_water_velocity','Northward_sea_water_velocity'] #NGOFS2
#snames_of_vars_to_include = ['sea_water_x_velocity','sea_water_y_velocity','upward_sea_water_velocity'] #ROMS
#snames_of_vars_to_include = None #don't filter vars

start = datetime.datetime(2023,9,22)
end = datetime.datetime(2023,9,25)
bbox = (-124.33,45.98,-123.06,46.41)
#bbox = utilities.get_example_bbox(model_id)

#Use model catalogs to get filelist from TDS
model_catalogs = False
if model_catalogs:
    model_source = 'coops-forecast-noagg'
    env_models = mc.setup()
    cat = env_models[model_id][model_source]
    source = mc.select_date_range(cat, start_date=start, end_date=end)
    fnames = [x.split('/')[-1] for x in source.urlpath]
else:
    fnames = aws.get_coops_flist_for_download(model_id,start,end)
    
#Download files from AWS
print('Downloading files from AWS')
filepaths = aws.download_from_coops_ofs(fnames,out_dir=out_dir)

#Subset and write new smaller files 


print('Subsetting and writing nc files')
newfiles = model_em.get_model_subset(filepaths,bounds=bbox,model_type=model_type,surface_only=True,out_dir=out_dir,snames_of_vars_to_include=snames_of_vars_to_include)

cmd = 'ncra -Y ncrcat ' + ' '.join(newfiles) + ' ' + model_id  + '.nc'
os.system(cmd)

#ofn = model_em.concat(newfiles,model_id + '.nc')


