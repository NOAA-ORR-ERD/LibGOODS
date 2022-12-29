from libgoods import api
import datetime

model_id = 'TBOFS'
model_source = 'coops-forecast-agg'
start = datetime.datetime.today()
end = start + datetime.timedelta(days=2)
bounds = [-82.9, 27.3, -82.6, 27.7]
env_params = ["surface currents", "surface winds"]
target_pth = 'tbofs_test.nc'

out_file = api.get_model_file(
    model_id,
    model_source,
    start,
    end,
    bounds,
    surface_only=True,
    environmental_parameters=env_params,
    # cross_dateline=False,
    # max_filesize=None,
    target_pth=target_pth)

