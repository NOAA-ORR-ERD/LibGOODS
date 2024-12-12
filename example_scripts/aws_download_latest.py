#!/usr/bin env python

import datetime
from libgoods import coops_ofs
import os
from pathlib import Path
import re

models_to_download = [#'WCOFS',
             # 'SSCOFS',
             # 'NGOFS2',
#             'CBOFS',
             'TBOFS',
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

    model_info = coops_ofs.OFS_INFO[model]

    out_dir = OFS_OUTPUT_DIR / model_info.identifier
    temp_dir = out_dir / "tmp"

    out_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)

    # get a list of the existing forecast files so they can be deleted later
    regex = re.compile(".[f][0-9]{3}.")
    if os.path.exists(out_dir):
        old_fc_list = [f for f in os.listdir(out_dir) if re.search(regex, f)]
    else:
        old_fc_list = []

    x_days_ago = datetime.timedelta(days=2)
    start = datetime.datetime.today() - x_days_ago
    end = start + datetime.timedelta(days=10)  # longest COOPS forecast is 120 hrs

    try:
        fnames = coops_ofs.get_aws_flist(model_info, start, end)
    except KeyError:
        print('2d files not available, downloading 3d')
        fnames = coops_ofs.get_aws_flist(model_info, start, end, file_type='fields')

    filepaths = coops_ofs.download_from_aws(model_info, fnames, out_dir=out_dir, temp_dir=temp_dir)

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
