from libgoods import model_nc4 as model
import datetime

# url = 'https://opendap.co-ops.nos.noaa.gov/thredds/dodsC/GOMOFS/fmrc/Aggregated_7_day_GOMOFS_Fields_Forecast_best.ncd'
url = "http://tds.ioos.us/thredds/dodsC/ioos/ofs/gomofs/forecast/fields/GoMOFS_Forecast_Fields_best.ncd"

start = datetime.datetime.today()
end = start + datetime.timedelta(days=1)
bounds = [-70, 41, -66, 44]

print('subsetting')
ds = model.get_model_subset(url,start,end,bounds,grid='ROMS',surface_only=True)

print('downloading output')
ofn = model.get_model_output(ds,'2d_test.nc')