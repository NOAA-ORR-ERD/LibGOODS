from libgoods import model_nc4 as model
import datetime

url = 'https://eds.ioos.us/thredds/dodsC/ioos/ofs/ngofs2/forecast/regulargrid/NGOFS2_Forecast_Regulargrid_best.ncd'
#url = "http://tds.ioos.us/thredds/dodsC/ioos/ofs/nyofs/forecast/fields/NYOFS_Forecast_Fields_best.ncd"

var_map = {'time':'time','longitude':'Longitude','latitude':'Latitude','eastward_sea_water_velocity':'u_eastward','northward_sea_water_velocity':'v_northward','mask':'mask'}
start = datetime.datetime.today()
end = start + datetime.timedelta(days=1)
bounds = [-90.8,28.76,-89.06,29.7]

print('subsetting')
ds = model.get_model_subset(url,start,end,bounds,var_map=var_map,grid='curvilinear',surface_only=True)

print('downloading output')
ofn = model.get_model_output(ds,'ngofsR_test.nc')