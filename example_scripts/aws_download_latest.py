#!/usr/bin env python

import datetime
import os
from pathlib import Path
import re

from libgoods import coops_ofs, scripting

'''
This was the original script (not using aws cli) to download the latest
batch of COOPS OFS files and populate a local directory. It does not
preserve the folder structure of the AWS bucket and hence won't work
with the libGOODS API as a local archive.

'''

how_many_days_back = 20


# Set up the logger:
scripting.initialize_console_log('info')  # debug gets a LOT from the AWS stuff


models_to_download = [#'WCOFS',
              # 'SSCOFS',
              'NGOFS2',
#             'CBOFS',
             #'TBOFS',
             # 'DBOFS',
             # 'GOMOFS',
             # 'CIOFS',
             # 'SFBOFS',
             # 'LEOFS',
             # 'LMHOFS',
             # 'LOOFS',
             # 'LSOFS'
             ]

OFS_OUTPUT_DIR = Path("OFS_results")

for model in models_to_download:

    out_dir = OFS_OUTPUT_DIR / model
    temp_dir = out_dir / "tmp"

    out_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    # get a list of the existing forecast files so they can be deleted later
    regex = re.compile(".[f][0-9]{3}.")
    if os.path.exists(out_dir):
        old_fc_list = [f for f in os.listdir(out_dir) if re.search(regex, f)]
    else:
        old_fc_list = []

    x_days_ago = datetime.timedelta(days=how_many_days_back)
    start = datetime.datetime.today() - x_days_ago
    end = start + datetime.timedelta(days=10)  # longest COOPS forecast is 120 hrs

    try:
        fnames = coops_ofs.get_aws_flist(model, start, end)
    except KeyError:
        print('2d files not available, downloading 3d')
        fnames = coops_ofs.get_aws_flist(model, start, end, file_type='fields')

    filepaths = coops_ofs.download_from_aws(model, fnames, out_dir=out_dir, temp_dir=temp_dir)

    # clean up old files and move new files once a new forecast is downloaded
    new_fc_list = [f for f in filepaths if re.search(regex, f)]
    if len(new_fc_list) == len(old_fc_list) or len(old_fc_list) == 0:
        useless_var = [os.remove(os.path.join(out_dir, fp)) for fp in old_fc_list]
        useless_var2 = [
            os.rename(os.path.join(temp_dir,
                                   os.path.split(fp)[-1]),
                      os.path.join(out_dir,
                                   os.path.split(fp)[-1])) for fp in filepaths
        ]
