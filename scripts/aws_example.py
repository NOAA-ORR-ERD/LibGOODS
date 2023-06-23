import model_catalogs as mc
import datetime
import os
from libgoods import aws, model_em

start = datetime.datetime.today()
end = start + datetime.timedelta(days=2)
bbox = (-91.5+360, 29.25, -91+360, 29.75)

#Use model catalogs to get filelist from TDS
env_models = mc.setup()
model_id = 'NGOFS2_2DS'
model_source = 'coops-forecast-noagg'

cat = env_models[model_id][model_source]
source = mc.select_date_range(cat, start_date=start, end_date=end)
fnames = [x.split('/')[-1] for x in source.urlpath]

#Download files from AWS
print('Downloading files from AWS')
filepaths = aws.download_from_coops_ofs(fnames)

#Subset and write new smaller files with only specific variables needed
#these are model specific - var_list is standard names
var_list = ['eastward_seasurface_water_velocity', 'Northward_seasurface_water_velocity']
drop_variables = ['Itime', 'Itime2']

print('Subsetting and writing nc files')
newfiles = model_em.get_model_subset(filepaths,start,end,bbox,var_list,drop_variables=drop_variables)

cmd = 'ncra -Y ncrcat ' + ' '.join(newfiles) + 'myAwesomeFile.nc'
os.system(cmd)




