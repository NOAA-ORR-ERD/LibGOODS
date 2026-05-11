import datetime
import os

from libgoods.file_processing import rect_model

url = 'https://pae-paha.pacioos.hawaii.edu/thredds/dodsC/wrf_cnmi/WRF_CNMI_Regional_Atmospheric_Model_best.ncd'
start = datetime.datetime.today()
end = datetime.datetime.today() + datetime.timedelta(days=3)

ds = rect_model.rect()
ds.open_nc(url)

var_map = {'time':'time','eastward_wind':'Uwind','northward_wind':'Vwind','longitude':'lon','latitude':'lat'}
ds.get_dimensions(var_map)

ts = ds.get_timeslice_indices(start, end)
ds.subset([119.79,12.04,124.83,14.97])

ofn = os.path.join('output','wrf.nc')
ds.write_nc(var_map,ofn,t_index=[ts[0],ts[1],1])

