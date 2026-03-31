import datetime
from libgoods import coops_ofs, models

'''
INCOMPLETE!

Hopefully we can use the aws syncing script now.

This script demonstrates downloading a time series of CCOOPS files from AWS and creating and working with a model object to subset and write
to a aggregated file for GNOME
'''
model_id = 'NGOFS2'
out_dir = 'ngofs2'
model_type = 'FVCOM'

start = datetime.datetime(2025,6,1,0,0)
end = datetime.datetime(2025,6,1,6,0)
bbox = (-124.2, 48.072,-123.64, 48.51)

fnames = coops_ofs.get_aws_flist(model_id, start, end, file_type='2ds')
# file type either 2ds or fields (3d)

# Download files from AWS
print('Downloading files from AWS')
flist = coops_ofs.download_from_aws(model_id, fnames, out_dir=out_dir)

m = models.ALL_MODELS[model_id]()
m.concat_dim = 'time'
m.ds = m.open_ds_local(flist)

try:
    m.select_surface() #not necessary if 2ds files specified in file_type
except ValueError:
    pass

m.subset_grid(bbox)
m.filter_variables()

m.write_nc('ngofs.nc')


