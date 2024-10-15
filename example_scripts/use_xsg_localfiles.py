#script demonstrating use of xaray-subset-grid with unaggregated local files

from libgoods import models, utilities, coops_ofs
import os
import datetime

model_id = 'SSCOFS'
model_type = 'FVCOM'    
driver = 'local'
ldir = os.path.join('.','output',model_id)

env_params = ["surface currents"]
start = datetime.datetime(2024,10,7,0,0)
end = start + datetime.timedelta(days=2)

coops = coops_ofs.coops(model_id,6)
flist = coops.get_local_flist(start,end,ldir,file_type='fields')

#!!!!!!!!!!TODO: write utility function that can do this in chunks for really large file lists that may exceed single command line capability
cdir = os.getcwd()
os.chdir(ldir)
cat_file = model_id  + '.nc'
cmd = 'ncra -Y ncrcat ' + ' '.join(flist) + ' ' + cat_file
os.system(cmd)
os.chdir(cdir)

bounds = utilities.get_example_bbox(model_id)
#bounds = (-122.8,47.27,-122.04,47.8)
   
if model_type == 'FVCOM': 
    m = models.fvcom()    
elif model_type == 'ROMS': 
    m = models.roms()    
else:
    raise NotImplementedError
    
m.open_ds(os.path.join(ldir,cat_file),driver=driver)
m.select_surface()
m.filter_variables()
m.subset_grid(bounds)
m.write_nc(os.path.join(ldir,model_id + '_subset.nc'))
    