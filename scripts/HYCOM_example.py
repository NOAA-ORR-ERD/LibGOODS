"""run HYCOM example"""
import json
import os
from libgoods import rect_model, temp_files_dir


with open('..\\libgoods\\current_sources\\hycom.json', 'r') as f:
  model_info = json.load(f)

url = model_info['url']
var_map = model_info['var_map']

hycom = rect_model.rect(url)

subset_box = [ #south lat, west lon, north lat, east lon
    46,
    -127,
    49,
    -123
]

hycom.get_dimensions(var_map)
hycom.when()


hycom.subset(subset_box)

ofn = os.path.join(temp_files_dir,'HYCOM.nc')
hycom.write_nc(var_map,ofn)
