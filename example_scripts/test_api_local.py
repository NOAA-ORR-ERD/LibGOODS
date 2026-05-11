import datetime
from pathlib import Path

from libgoods import api, config

# Test uisng local version of libgoods archive
local_archive_dir = Path.cwd().parent.parent / 'webgnomeapi' / 'libgoods-cache'

config.archive_dir = local_archive_dir

# need to add sfbofs in once we support that
local_models = ['wcofs', 'sscofs', 'ngofs2', 'cbofs', 'tbofs', 'dbofs', 'sfbofs',
                    'gomofs', 'ciofs',  'leofs', 'loofs', 'lmhofs', 'lsofs']


ep = ['surface currents']
sizes = []

for ofs in local_models:
    print(ofs)
    ofn = Path.cwd() / 'output' / ''.join([ofs,'.nc'])

    if not ofn.exists():

        # get the model to determine actual start/end for models in local testing archive which may be out of date
        # Also to get the example bounds from the metadata
        m = api.get_model(ofs.upper())
        bounds = m.metadata.bounding_box
        if m.access == 'local':
            start = m.actual_start
            end = m.actual_end
        else:
            start = datetime.datetime.today()
            end = start + datetime.timedelta(days=1)

        ds = api.get_model_subset(ofs.upper(), start=start, end=end, bounds=bounds, environmental_parameters=ep)
        print(ds.size()/1e6)
        sizes.append(ds.size()/1e6)
        api.get_model_output(ds, str(ofn))

    else:

        print('Output already exists - skipping')

    print('DONE')

    for ii in range(len(sizes)):
        print(local_models[ii])
        print(sizes[ii])

