"""
A test of subsetting the NGOFS2 for surface currents
"""

import datetime

from libgoods import api
from pathlib import Path

HERE = Path(__file__).parent

# Region: (just of southwest pass
bounds = ((-89.50, 28.85), ( -89.35, )) # lower-left, upper-right
north =  28.95
south =  28.85
west =  -89.50
east =  -89.35
bounds = ((west, south), (east, north))

now = datetime.datetime.now()
now = now.replace(hour=12, minute=0, second=0, microsecond=0)
start_time = now - datetime.timedelta(days=2)
end_time = now + datetime.timedelta(days=1)


Model = api.get_model_subset(
    'NGOFS2',
    start=start_time,
    end=end_time,
    bounds=bounds,
    environmental_parameters=['surface currents'],
)

Model.write_nc(HERE / "NGOFS2_subset.nc")



