import datetime
from libgoods import coops_ofs, models

model_id = 'NGOFS2'
out_dir = 'ngofs2'
model_type = 'FVCOM'

start = datetime.datetime(2025,6,1,0,0)
end = datetime.datetime(2025,6,1,6,0)
bbox = (-124.2, 48.072,-123.64, 48.51)

fnames = coops_ofs.get_aws_flist(model_id, start, end, file_type='2ds')
# Download files from AWS
print('Downloading files from AWS')
flist = coops_ofs.download_from_aws(model_id, fnames, out_dir=out_dir)

m = models.ALL_MODELS[model_id]()
m.ds = m.open_ds_local(flist)

m.select_surface()
m.subset_grid(bbox)
m.filter_variables()

m.write_nc('sscofs.nc')


