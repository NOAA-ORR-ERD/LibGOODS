'''
Downloading each file separately
'''

import model_catalogs as mc
import datetime
from libgoods import file_processing
import time
from pathlib import Path

output_dir = Path('TBOFS_results')
output_dir.mkdir(exist_ok=True)


main_cat = mc.setup() #just using model_catalogs to get the url list
bounds = [-82.9, 27.3, -82.6, 27.7]
model_id = 'TBOFS'
model_source = 'coops-forecast-noagg'
cat = main_cat[model_id][model_source]

start = datetime.datetime.today()
end = (start + datetime.timedelta(days=2))

print("Calling select_date_range")
mc.select_date_range(cat,start_date=start,end_date=end) #this could alternatively be done on the xarray ds

urls = cat.urlpath

print("Downloading")
t0 = time.time()
for count, url in enumerate(urls):
    print(f"{count + 1} of {len(urls)}")
    if count == 0:
        model = file_processing.roms()
        var_map = {"time": "ocean_time"}
        model.open_nc(url)
        model.get_dimensions(var_map=var_map)
        model.subset(bounds)
    # else:
    #     model.update(url)

    num_fails = 0
    while num_fails < 5:
        model.update(url)
        try:
            ofn = output_dir / f'tbofs_nc_{count:0>3}.nc'
            model.write_nc(var_map=var_map, ofn=ofn)
            break
        # seems to be different type each time :-(
        except Exception as err:
            num_fails += 1
            print(f"problem with Server:\n {ofn} {num_fails} times")
            print(type(err), err)



t1 = time.time()
print(f"Process took: {(t1-t0)/60: .2f} minutes")
