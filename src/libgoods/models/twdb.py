import datetime
import urllib
import requests
from requests.exceptions import Timeout
import zipfile
import tempfile, os
import numpy as np
import re

'''
These are provided as zip files downloaded from a URL - we could add an api that allows subsetting similar to others but I'm not sure we need it as they are not very big and being replaced by SELFE versions.
U/V are depth averaged.

NOTE: the server appears to be down or no longer supported
'''

models = ['Sabine', 'Galv', 'Matag' , 'CCBay', 'CopSA']
base_url = r"http://midgewater.twdb.texas.gov/bays_estuaries/GNOME/MostRecent/"

class BaseTWDB:

    html_info = r'The <a href="http://www.twdb.texas.gov/index.asp" target="_blank"> Texas Water Development Board (TWDB)</a>, in partnership with the <a href="http://www.glo.texas.gov/" target="_blank"> Texas General Land Office (TGLO) </a> Oil Spill Prevention and Response effort, maintains <a href="http://www.twdb.texas.gov/surfacewater/bays/oil_spill/index.asp" target="_blank"> near real-time and forecast simulations of water circulation in the major bays </a> for use in the event that an oil spill occurs within Texas bays.'

    def __init__(self):
        # Fixme: this prob ably shouldn't do this on init -- but rather when asked to shcek, or ?
        self.urls = {}
        r = requests.get(base_url, timeout=1)
        if not r.ok:
            self.urls = {model: 'URL not found' for model in models}
        else:
            html_text = r.text
            for model in models:
                fname = re.search(model+r'.\d{6}.\d{2}.zip',html_text).group()
                self.urls[model] = base_url + fname

    def open_ds(self):
        print('Not implemented yet - model files are downloaded via http by calling write_nc')

    def subset_time(self,start,end):
        print('Not implemented yet - model files are downloaded via http by calling write_nc')

    def subset_grid(self,bbox):
        print('Not implemented yet - model files are downloaded via http by calling write_nc')

    def write_nc(self,ofn=None):
        u = urllib.request.urlopen(self.location)
        tfn = tempfile.mktemp(suffix='.zip')
        tzip = open(tfn, 'wb')
        tzip.write(u.read())
        tzip.close()
        if ofn == None:
            ofn = self.name.replace(" ","") + '.nc'
        zfile = zipfile.ZipFile(tfn)
        for ii,f in enumerate(zfile.filelist):
            if f.filename == 'currents.nc':
                f.filename = ofn
                index = ii

        zfile.extract(zfile.filelist[index])
        zfile.close()


class SabineLake(BaseTWDB):

    def __init__(self):
        super().__init__()       
        self.location = self.urls['Sabine']
        self.name = 'Sabine Lake'

class GalvestonBay(BaseTWDB):   
    
    def __init__(self):
        super().__init__()       
        self.location = self.urls['Galv']
        self.name = 'Galveston Bay'

class MatagordaBay(BaseTWDB):   
    
    def __init__(self):
        super().__init__()       
        self.location = self.urls['Matag']
        self.name = 'Matagorda Bay'
      
class CorpusChristiBay(BaseTWDB):   
    
    def __init__(self):
        super().__init__()       
        self.location = self.urls['CCBay']
        self.name = 'Corpus Christi Bay'
        
class SanAntonioBay(BaseTWDB):   
    
    def __init__(self):
        super().__init__()       
        self.location = self.urls['CopSA']
        self.name = 'San Antonio Bay'
        
