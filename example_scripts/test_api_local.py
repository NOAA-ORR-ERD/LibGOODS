from libgoods import api, config, models
import datetime
from pathlib import Path

# Test uisng local version of libgoods archive
local_archive_dir = lg = Path.cwd().parent / 'experiments' / 'libgoods-cache'

config.archive_dir = local_archive_dir

# need to add sfbofs in once we support that
supported_models = ['wcofs', 'sscofs', 'ngofs2', 'cbofs', 'tbofs', 'dbofs', 'sfbofs',
                    'gomofs', 'ciofs',  'leofs', 'loofs', 'lmhofs', 'lsofs', 'espc',
                    'tamu','gfs']


for ofs in supported_models:
    print(ofs)
    ofn = Path.cwd() / 'output' / ''.join([ofs,'.nc'])

    if not ofn.exists():

        # get the model to determine actual start/end for models in local testing archive which may be out of date
        # Also to get the example bounds from the metadata
        m = api.get_model(ofs.upper())
        bounds = m.metadata.example_bbox
        if m.access == 'local':
            start = m.actual_start
            end = m.actual_end
        else:
            start = datetime.datetime.today()
            end = start + datetime.timedelta(days=1)

        if bounds is not None:
            if ofs == 'gfs':
                ds = api.get_model_subset(ofs.upper(), start=start, end=end, bounds=bounds, \
                                          environmental_parameters=["surface winds"])
            else:
                ds = api.get_model_subset(ofs.upper(), start=start, end=end, bounds=bounds)

            api.get_model_output(ds, str(ofn))
        else:
            print('No bounds')
    else:

        print('Output already exists - skipping')

    print('DONE')

