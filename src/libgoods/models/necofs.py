from .base_xsg import FVCOM
from .metadata import Metadata

'''
This is a work in progress -- subsetting over OPeNDAP is no bueno so we
do a download of the whole file first (can select just the surface, narrow time,
and filter relevant vars)

'''
class BaseNECOFS(FVCOM):
    access = "opendap"
    standard_names = FVCOM.standard_names.copy()

    def download_from_tds(self, start_time=None, end_time=None, surface_only=True,
                filter_vars=True):
        # specialized case to download the full grid file
        # then reopen locally for grid subsetting
        ds = self.open_ds_tds(self.location)
        self.ds = ds
        if start_time is not None and end_time is not None:
            # TO DO - make subset_time accept start or end None
            self.subset_time(start_time, end_time)
        if surface_only:
            #self.select_surface()
            self.ds = self.ds.isel(siglay=0)
        if filter_vars:
            self.filter_variables()
        print("Downloading file")
        self.write_nc("necofs_fullgrid.nc")
        self.ds = None
        self.location = "necofs_fullgrid.nc"



class NECOFS(BaseNECOFS):
    metadata = Metadata()
    metadata.identifier = 'NECOFS'
    metadata.name = "Northeast Coastal Ocean Forecast (GOM7)"
    location = "http://www.smast.umassd.edu:8080/thredds/dodsC/models/fvcom/NECOFS/Forecasts/NECOFS_GOM7_FORECAST.nc"
    metadata.example_bbox = (-70, 41, -66, 44)


class MassCoastal(BaseNECOFS):
    metadata = Metadata()
    metadata.identifier = 'MassCoastal'
    metadata.name = "Massachusetts Coastal Model"
    location = "http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc"


class BostonHarbor(BaseNECOFS):
    metadata = Metadata()
    metadata.identifier = 'BostonHarbor'
    metadata.name = "Boston Harbor, MA"
    location = "http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_BOSTON_FORECAST.nc"


class Hampton(BaseNECOFS):
    metadata = Metadata()
    metadata.identifier = 'Hampton'
    metadata.name = "Hampton, NH"
    location = "http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_HAMPTON_FORECAST.nc"


class Scituate(BaseNECOFS):
    metadata = Metadata()
    metadata.identifier = 'Scituate'
    metadata.name = "Scituate, MA"
    location = "http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_SCITUATE_FORECAST.nc"
