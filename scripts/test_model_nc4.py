from libgoods import model_nc4 as model
import datetime

url = 'https://opendap.co-ops.nos.noaa.gov/thredds/dodsC/CBOFS/fmrc/Aggregated_7_day_CBOFS_Fields_Forecast_best.ncd'

start = datetime.datetime.today()
end = start + datetime.timedelta(days=1)
bounds = [-76.5, 36.75, -75.25, 37.75]

print('subsetting')
ds = model.get_model_subset(url,start,end,bounds,grid='ROMS',surface_only=True)

print('downloading output')
ofn = model.get_model_output(ds,'2d_test.nc')