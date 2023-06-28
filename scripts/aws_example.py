import model_catalogs as mc
import datetime
import os
from libgoods import aws, model_em, utilities

model_id = 'NGOFS2'
model_source = 'coops-forecast-noagg'
out_dir = 'ngofs'
model_type = 'FVCOM'

start = datetime.datetime.today()
end = start + datetime.timedelta(days=2)

bbox = utilities.get_example_bbox(model_id)


#Use model catalogs to get filelist from TDS
env_models = mc.setup()


cat = env_models[model_id][model_source]
source = mc.select_date_range(cat, start_date=start, end_date=end)
fnames = [x.split('/')[-1] for x in source.urlpath]

#Download files from AWS
print('Downloading files from AWS')
filepaths = aws.download_from_coops_ofs(fnames,out_dir=out_dir)

#Subset and write new smaller files 


print('Subsetting and writing nc files')
newfiles = model_em.get_model_subset(filepaths,start,end,bbox,model_type=model_type,surface_only=True,out_dir=out_dir)

cmd = 'ncra -Y ncrcat ' + ' '.join(newfiles) + ' ' + model_id  + '.nc'
os.system(cmd)




