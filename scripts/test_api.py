from libgoods import api
import datetime
import os

model_id = 'CBOFS'
model_source = 'coops-forecast-agg'

start = datetime.datetime.today()
end = start + datetime.timedelta(days=1)
bounds = [-76.5, 36.75, -75.25, 37.75] #CBOFS
#bounds = [-82.9, 27.3, -82.6, 27.7] #TBOFS

print('subsetting')
ds = api.get_model_subset(model_id,model_source,start,end,bounds,surface_only=True,environmental_parameters=["surface currents","surface winds"])

print('downloading output')
ofn = os.path.join('output','CBOFS.nc')
ofn = api.get_model_output(ds,ofn)

