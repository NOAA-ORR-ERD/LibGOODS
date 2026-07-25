"""
This script is an example  of  how to get a hindcast from the
Navy ESPC model

The default server only has an aggregation for 10 days or so in
the past, so if you need a longer hindcast, you need to change
what server is hit.
"""

from libgoods.models import ESPC


bbox = [(175.0, 48.0), (186.0, 56.0)]

start_time = "2026, 6, 23"
end_time = "2026, 7, 17"

model = ESPC()
model.location = 'https://tds.ioos.us/thredds/dodsC/ioos/hycom_navy/Navy_HYCOM_best.ncd'

model.open_ds()

print(model.actual_start)
print(model.actual_end)

model.subset_grid(bbox)
model.subset_time(start_time, end_time)



