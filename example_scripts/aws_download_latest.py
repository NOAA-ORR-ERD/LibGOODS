import datetime
from libgoods import coops_ofs
import os
import re

model_ids = ['WCOFS','SSCOFS','NGOFS2','CBOFS','TBOFS','DBOFS','GOMOFS','CIOFS','SFBOFS','LEOFS','LMHOFS','LOOFS','LSOFS']


for model_id in model_ids:
    
    print(model_id)
    if model_id == 'WCOFS':
        update_cycle=24
    else:
        update_cycle=6
        
    out_dir = os.path.join('output',model_id)
    temp_dir = os.path.join(out_dir,'tmp')

    #get a list of the existing forecast files so they can be deleted later
    regex = re.compile(".[f][0-9]{3}.")
    if os.path.exists(out_dir):
        old_fc_list = [f for f in os.listdir(out_dir) if re.search(regex, f)]
    else:
        old_fc_list = []

    x_days_ago = datetime.timedelta(days=2)
    start = datetime.datetime.today() - x_days_ago
    end = start + datetime.timedelta(days=10) #longest COOPS forecast is 120 hrs

    m = coops_ofs.coops(model_id)      
    try:        
        fnames = m.get_aws_flist(start,end)        
    except KeyError:
        print('2d files not available, downloading 3d')
        fnames = m.get_aws_flist(start,end,file_type='fields')

    filepaths = m.download_from_aws(fnames,out_dir=out_dir,temp_dir=temp_dir)

    #clean up old files and move new files once a new forecast is downloaded
    new_fc_list = [f for f in filepaths if re.search(regex, f)]
    if len(new_fc_list) == len(old_fc_list) or len(old_fc_list)==0:
        useless_var = [os.remove(os.path.join(out_dir,fp)) for fp in old_fc_list]
        useless_var2 = [os.rename(os.path.join(temp_dir,os.path.split(fp)[-1]),os.path.join(out_dir,os.path.split(fp)[-1]))  for fp in filepaths]






