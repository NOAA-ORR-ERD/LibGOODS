import json
import os
from libgoods import roms_model, temp_files_dir
from importlib import reload
reload(roms_model)

with open('..\\libgoods\\currents\\tbofs.json', 'r') as f:
  model_info = json.load(f)

url = model_info['url']
var_map = model_info['var_map']

tbofs = roms_model.roms(url)

subset_box = [ #south lat, west lon, north lat, east lon
    27.499,
    -82.827,
    27.725,
    -82.607
]

tbofs.get_dimensions(var_map['time'])
tbofs.when()


tbofs.subset(subset_box) 



 

