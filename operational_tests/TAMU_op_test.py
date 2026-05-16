"""
A test of subsetting the GFS for surface winds
"""
import datetime
from pathlib import Path
from libgoods import api

HERE = Path(__file__).parent

TAMU = api.get_model('TAMU')

end_time = TAMU.actual_end
start_time = end_time - datetime.timedelta(days=2)

bounds = TAMU.metadata.example_bbox

# bounds = ((west, south), (east, north))

#fixme: should probably update this with a today-relative datetime.

# # See what's there:
# all_models = api.list_model_names()

# for m in all_models:
#     print(m)

# # get the GFS:
# GFS = api.get_model('GFS')
# print(GFS)

Model = api.get_model_subset(
    'TAMU',
    bounds=bounds,
    start=start_time,
    end=end_time,
    environmental_parameters=['surface currents'],
)

Model.write_nc(HERE / "TAMU_subset.nc")



