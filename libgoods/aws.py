import requests
import os

def download_from_coops_ofs(fnames,out_dir='temp_files'):
    '''
    NOS OFS are available in an AWS S3 bucket at:
    https://noaa-nos-ofs-pds.s3.amazonaws.com/index.html

    You can browse around and see what’s there in a big heap of files. To generate a list of files to download (a time series) you can leverage some of the code in model_catalogs to get the list of files.

    Parameters
    ----------
    
    fnames : list of filenames (str)
    
    '''
    
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    aws_url = 'https://noaa-nos-ofs-pds.s3.amazonaws.com/'
    newfilenames = []
    for fname in fnames:
        out_file =  os.path.join(out_dir,fname)
        if os.path.exists(out_file):
            print('Already downloaded', fname)
        else:
            yyyymmdd = fname.split('.')[4]      
            model_id = fname.split('.')[1]
            url = aws_url + model_id + '/netcdf/' + yyyymmdd[0:6] + '/' + fname
            print(url)
            r = requests.get(url)
            #resp = http.request("GET", url, preload_content=False)
            
            if r.headers['Content-Type'] == 'application/xml':
                print(r.content)
            else:
                
                with open(out_file,'wb') as f:
                    f.write(r.content)
        newfilenames.append(out_file)            
    return newfilenames