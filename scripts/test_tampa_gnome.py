"""
test script for running PyGNOME with the tampa files downloaded
"""
from pathlib import Path
import gnome.scripting as gs

# from multifile download
# not working -- duplicate entries in time series
# current_file = [Path("TBOFS_results") / f"tbofs_nc_{i:0>3}.nc"
#                 for i in range(48)]

current_file = "test_tbofs_dask_single_threded.nc"

mapfile = "tampa_shoreline.bna"

curr_mover = gs.PyCurrentMover(current_file)

map = gs.MapFromBNA(mapfile)

bounds = (map.map_bounds.min(axis=0), map.map_bounds.max(axis=0)

