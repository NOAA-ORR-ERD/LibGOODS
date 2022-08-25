"""
Code for getting GNOME maps

Notes:

we may want to be smarter about how to handle big files.
 - Perhaps the API could take a path to write to, so it can
   write data bit by bit, and do checks for file size, etc

We should use the requests package if we have to do much
querying of other systems
"""

import urllib
import urllib.request

from . import utilities

GOODS_URL = "https://gnome.orr.noaa.gov/goods/"


class FileTooBigError(ValueError):
    pass


RESOLUTIONS = {
    "i",
}


def get_map(
    bounds,
    resolution="h",
    shoreline="gshhs",
    cross_dateline=False,
    max_filesize=None,
):
    """get map"""
    bbox = utilities.polygon2bbox(bounds)

    # south_lat, west_lon, north_lat, east_lon = bbox
    (west_lon, south_lat), (east_lon, north_lat) = bbox

    print(west_lon, south_lat, east_lon, north_lat)

    utilities.check_valid_box(bbox)

    # if resolution == "appropriate":
        # raise NotImplementedError(
            # "libgoods can not yet determine the appropriate resolution for you"
        # )

    # this is what the current GOODS API requires
    req_params = {
        "err_placeholder": "",
        "NorthLat": north_lat,
        "WestLon": west_lon,
        "EastLon": east_lon,
        "SouthLat": south_lat,
        "xDateline": int(cross_dateline),
        "resolution": resolution,
        "submit": "Get Map",
    }

    query_string = urllib.parse.urlencode(req_params)
    data = query_string.encode("ascii")
    url = GOODS_URL + "tools/" + shoreline.upper() + "/coast_extract"

    # url = url + "?" + query_string

    # with urllib.request.urlopen( url ) as response:
    #     response_text = response.read()
    #     print( response_text )

    goods_resp = urllib.request.urlopen(url, data)

    filename = goods_resp.headers.get_filename()

    size = goods_resp.length

    if (max_filesize is not None) and size > max_filesize:
        raise ValueError(f"File is too big! Max size = {max_filesize}")

    contents = goods_resp.read().decode("utf-8")

    goods_resp.close()

    return filename, contents
