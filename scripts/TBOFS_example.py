import json
import os
from libgoods import roms_model, temp_files_dir


with open('..\\libgoods\\current_sources\\tbofs.json', 'r') as f:
  model_info = json.load(f)

url = model_info['url']

tbofs = roms_model.roms(url)

subset_box = [ #south lat, west lon, north lat, east lon
    27.499,
    -82.827,
    27.725,
    -82.607
]

tbofs.get_dimensions()
tbofs.when()

tbofs.subset(subset_box) 
ofn = os.path.join(temp_files_dir,'TBOFS.nc')
tbofs.write_nc(var_map=None,ofn=ofn)


 

