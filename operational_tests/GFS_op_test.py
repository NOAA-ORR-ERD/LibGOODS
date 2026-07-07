"""
A test of subsetting the GFS for surface winds
"""

import datetime

from libgoods import api
from pathlib import Path

HERE = Path(__file__).parent

# Region: (east coast)
north =  40.718059
south =  38.692026
west =  -73.802384
east =  -69.889183
bounds = ((west, south), (east, north))

now = datetime.datetime.now()
now = now.replace(hour=12, minute=0, second=0, microsecond=0)
start_time = now - datetime.timedelta(days=1)
end_time = now + datetime.timedelta(days=2)


# # See what's there:
# all_models = api.list_model_names()

# for m in all_models:
#     print(m)

# # get the GFS:
# GFS = api.get_model('GFS')
# print(GFS)

Model = api.get_model_subset(
    'GFS',
    start=start_time,
    end=end_time,
    bounds=bounds,
    environmental_parameters=['surface winds'],
)

Model.write_nc(HERE / "GFS_subset.nc")



