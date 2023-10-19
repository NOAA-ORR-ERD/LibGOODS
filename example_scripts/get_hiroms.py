from libgoods.file_processing import roms_model
import datetime
import os

url = 'https://pae-paha.pacioos.hawaii.edu/thredds/dodsC/pacioos/roms_native/mari/ROMS_CNMI_Regional_Ocean_Model_Native_Grid_best.ncd'

start = datetime.datetime.today()
end = datetime.datetime.today() + datetime.timedelta(days=3)

ds = roms_model.roms()
ds.open_nc(url)
 
var_map = {'time':'time'}
ds.get_dimensions(var_map)

ts = ds.get_timeslice_indices(start, end)
ds.subset([119.79,12.04,124.83,14.97])

ofn = os.path.join('output','hiroms.nc')
ds.write_nc(var_map,ofn,t_index=[ts[0],ts[1],1])
