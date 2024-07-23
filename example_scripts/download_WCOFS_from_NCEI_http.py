from pathlib import Path
import requests
from datetime import datetime

base_url = "https://www.ncei.noaa.gov/data/operational-nowcast-and-forecast-hydrodynamic-model-systems-co-ops/access/west-coast-operational-forecast-system-wcofs/"

# full https://www.ncei.noaa.gov/data/operational-nowcast-and-forecast-hydrodynamic-model-systems-co-ops/access/west-coast-operational-forecast-system-wcofs/2021/03/nos.wcofs.2ds.n013.20210322.t03z.nc
#      https://www.ncei.noaa.gov/data/operational-nowcast-and-forecast-hydrodynamic-model-systems-co-ops/access/west-coast-operational-forecast-system-wcofs/2021/03/nos.wcofs.2ds.n001.202100322.t03z.nc'
# example file name
#nos.wcofs.2ds.n001.20210324.t03z.nc

#2021/03/

out_dir = Path('WCOFS_archive')
out_dir.mkdir(exist_ok=True)

year = 2021
month = 3

n = 1
day = 22
# for year in (2021, 2022, 2023):
for year in (2022, 2023):
    for month in range(1, 13):
        for day in range(1, 32):
            for n in range(1, 25):
                url = f"{base_url}{year}/{month:02}/"

                filename = f"nos.wcofs.2ds.n{n:03}.{year}{month:02}{day:02}.t03z.nc"

                local_path = (out_dir / filename)

                # NOTE: They are not all exactly the same size -- so making sure it's at least close
                # if it's already there, and the right size, skip it
                if local_path.is_file() and local_path.stat().st_size >= 72070000:
                    print("skipping: ", filename)
                    continue

                print("attempting to download:", filename)

                full_url = f"{url}{filename}"

                start = datetime.now()
                req = requests.get(full_url)
                if req.status_code == 200:
                    open(local_path, 'wb').write(req.content)
                    print(f"got it in {(datetime.now() - start).total_seconds():.2f} seconds")
                else:
                    print("File not there")




