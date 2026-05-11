
"""
Amy's results:

Just currents: 513590632
Winds and Currents: 2946186892
 - five times as big

Chris's results:
Just currents:  87549492
Winds and Currents: 175167628
"""



import datetime

import xarray_subset_grid as xsg

from libgoods import api, config

config.archive_dir = "./libgoods-cache"

m = api.get_model('GOMOFS')
print(f"{m.access=}")

end = datetime.datetime.today()
start = end - datetime.timedelta(days=2)
bounds = (-69.38, 40.95, -60.97, 45.48)

for ep in [['surface currents'],
           ['surface winds'],
           ['surface currents', 'surface winds'],
           ]:

    m = api.get_model_subset('GOMOFS', start=start, end=end, bounds=bounds,
                             environmental_parameters=ep)
    print(f"{ep} total size:{xsg.utils.format_bytes(m.ds.nbytes)}")
    fname = "_".join(ep).replace(" ", "_") + ".nc"
    print("writing:", fname)
    m.write_nc(fname)

# ep = ['surface currents']
# m = api.get_model_subset('GOMOFS', start=start, end=end, bounds=bounds, environmental_parameters=ep)
# m.ds.nbytes
