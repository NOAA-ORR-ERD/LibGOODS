from libgoods import api
import datetime
import os

ax = False #True to use dask/xarry; False to use nc4

model_id = 'TBOFS'
model_source = 'coops-forecast-agg'
start = datetime.datetime.today()
end = start + datetime.timedelta(days=2)
bounds = [-82.9, 27.3, -82.6, 27.7]
env_params = ["surface currents", "surface winds"]
target_pth =  os.path.join('output','tbofs_test2.nc')

    
ds = api.get_model_subset(
    model_id,
    model_source,
    start,
    end,
    bounds,
    surface_only=True,
    cross_dateline=False,
    environmental_parameters=env_params,
    axiom=ax)

ofn = api.get_model_output(ds, target_pth, axiom=ax)
