from datetime import datetime, timedelta

import requests

from .base_xsg import FVCOM
from .metadata import Metadata


class BaseWFS(FVCOM):
    # might not need this base class -- we'll see

    access = "opendap"


class WFCOM(BaseWFS):
    metadata = Metadata()
    metadata.identifier = 'WFCOM'
    metadata.name = "West Florida Coastal Ocean Circulation Model"
    metadata.example_bbox = (-82.0, 24.0, -81.0, 26.0)

    locbase = "http://ocgtds.marine.usf.edu:8080/thredds/dodsC/WFCOM4_NF_model/WFCOM4_NF_"
    day_str = datetime.today().strftime("%Y%m%d")

    tbc_url = "http://ocgtds.marine.usf.edu:8080/thredds/catalog/WFCOM4_NF_model/catalog.html"
    html_text = requests.get(tbc_url).text
    while html_text.find("WFCOM4_NF_" + day_str + ".nc") == -1:
        day_str = (datetime.strptime(day_str, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")

    location = locbase + day_str + ".nc"


class TBCOM(BaseWFS):
    metadata = Metadata()
    metadata.identifier = 'TBCOM'
    name = "Tampa Bay Coastal Ocean Model"
    example_bbox = (-82.75, 27.5, -82.4, 27.75)
    # location = 'http://ocgtds.marine.usf.edu:8080/thredds/dodsC/TBCOM2_NF_model/TBCOM2_NF_20250327.nc'

    locbase = "http://ocgtds.marine.usf.edu:8080/thredds/dodsC/TBCOM2_NF_model/TBCOM2_NF_"
    day_str = datetime.today().strftime("%Y%m%d")

    tbc_url = "http://ocgtds.marine.usf.edu:8080/thredds/catalog/TBCOM2_NF_model/catalog.html"
    html_text = requests.get(tbc_url).text
    while html_text.find("TBCOM2_NF_" + day_str + ".nc") == -1:
        day_str = (datetime.strptime(day_str, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")

    location = locbase + day_str + ".nc"
