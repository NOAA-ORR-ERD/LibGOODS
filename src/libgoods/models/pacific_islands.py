
from .base_xsg import ROMS
from .metadata import Metadata

tds_url = "http://pae-paha.pacioos.hawaii.edu/thredds"


# To see what's there -- use this link: http://pae-paha.pacioos.hawaii.edu//thredds/roms_native.html
class PacIOOS(ROMS):
    standard_names = ROMS.standard_names.copy()
    tvar = "time"
    drop_variables = ["ocean_time", "dstart"]
    # ocean_time causes problems in output file if included (vars are aggregated on "time")
    # - the dstart is an issue b/c *some* of the files have calendar attribute messed up
    # (gregorian_proleptic instead of proleptic_gregorian) and since we don't need it anyway,
    # we're dropping it
    access = "opendap"
    standard_names["surface_eastward_sea_water_velocity"] = "u"
    standard_names["surface_northward_sea_water_velocity"] = "v"


class HIIG(PacIOOS):
    metadata = Metadata()
    metadata.identifier = 'HIIG'
    metadata.name = "Hawaiian Islands 4 km"
    location = (
        tds_url
        + "/dodsC/hioos/roms_native/hiig/ROMS_Hawaii_Regional_Ocean_Model_Native_Grid_best.ncd"
    )
    example_bbox = (-155.65, 19.2, -154, 20, 56)


class HIOG(PacIOOS):
    metadata = Metadata()
    metadata.identifier = 'HIOG'
    metadata.name = "Oahu 1 km"
    location = (
        tds_url
        + "/dodsC/hioos/roms_native/hiog/ROMS_Oahu_Regional_Ocean_Model_Native_Grid_best.ncd",
    )


class HIOMSG(PacIOOS):
    metadata = Metadata()
    metadata.identifier = 'HIOMSG'
    metadata.name = "Oahu South Shore"
    location = (
        tds_url
        + "/dodsC/hioos/roms_native/hiomsg/ROMS_Oahu_South_Shore_Regional_Ocean_Model_Native_Grid_best.ncd"  # noqa
    )


class HIOMSAG(PacIOOS):
    metadata = Metadata()
    metadata.identifier = 'HIOMSAG'
    metadata.name = "Waikiki"
    location = (
        tds_url
        + "/dodsC/hioos/roms_native/hiomsag/ROMS_Waikiki_Regional_Ocean_Model_Native_Grid_best.ncd"
    )


class HIOEKG(PacIOOS):
    metadata = Metadata()
    metadata.identifier = 'HIOEKG'
    metadata.name = "Kaneohe Bay"
    location = (
        tds_url
        + "/dodsC/hioos/roms_native/hioekg/ROMS_Kaneohe_Regional_Ocean_Model_Native_Grid_best.ncd"
    )


class WPAC(PacIOOS):
    metadata = Metadata()
    metadata.identifier = 'WPAC'
    metadata.name = "Western North Pacific"
    location = (
        tds_url
        + "/dodsC/pacioos/roms_native/wpac/ROMS_Western_North_Pacific_Regional_Ocean_Model_Native_Grid_best.ncd"
    )


class MARIG(PacIOOS):
    metadata = Metadata()
    metadata.identifier = 'MARIG'
    metadata.name = "Guam and Northern Mariana Islands"
    location = (
        tds_url
        + "/dodsC/pacioos/roms_native/marig/ROMS_Guam_Regional_Ocean_Model_Native_Grid_best.ncd"
    )


class SAMOA(PacIOOS):
    metadata = Metadata()
    metadata.identifier = 'SAMOA'
    metadata.name = "Samoa"
    location = (
        tds_url
        + "/dodsC/pacioos/roms_native/samoa/ROMS_Samoa_Regional_Ocean_Model_Native_Grid_best.ncd"
    )
