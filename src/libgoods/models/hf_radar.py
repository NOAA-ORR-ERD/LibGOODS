from .base_xsg import XSGBaseModel
from .metadata import Metadata

url_base = "https://dods.ndbc.noaa.gov/thredds/dodsC/"

# Note: access just changed to NDBC and folder structure is much simpler -- this mapping no longer used
# but still checking that input region is a key here
regions = {
    "AKNS": "Alaska_-_North_Slope",
    "GAK": "US_Gulf_of_Alaska",
    "USWC": "US_West_Coast",
    "USEGC": "US_East_and_Gulf_Coast",
    "USHI": "US_Hawaii",
    "PRVI": "Puerto_Rico_and_the_US_Virgin_Islands",
    "GLNA": "Great_Lakes_of_North_America",
}


class HFRadar(XSGBaseModel):
    chunks = None
    drop_variables = None
    standard_names = {
        "eastward_sea_water_velocity": "u",
        "northward_sea_water_velocity": "v",
    }
    tvar = "time"
    access = "opendap"
    is3d = False
    metadata = Metadata()
    metadata.identifier = 'HFRadar'

    def __init__(self, region=None, res="6km"):
        """
        Regions - must be key from dict above
        Resolution - 500m, 1km, 2km, 6km
        This only handles hourly - can add averages in future
        but URLs are inconsistent for 25h, monthly, annual

        """
        super().__init__(is3d=False)
        if region in regions:
            self.location = url_base + 'hfradar_' + region.lower() + '_' + res
        else:
            print("HFRadar: Region must be in ", list(regions.keys()))
            self.location = None
