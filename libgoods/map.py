"""
placeholder / mockup for libgoods

For the moment, this is where we will define the interaction between the
webgnome_api and libgoods.


Notes:

we may want to be smarter about how to handle big files.
 - Perhaps the API could take a path to write to, so it can
   write data bit by bit, and do checks for file size, etc

Do we want to have a boudnign boax as a single item?
 - either a special class -- we have one in py_gnome,
 - or a tuple of tuples.

Alterntaively, use a polygon for bounds
 -- it could happen to be a rectangle, or not.

We should use the requests package if we have to do much
querying of other systems

"""

import urllib

GOODS_URL = 'https://gnome.orr.noaa.gov/goods/'


class FileTooBigError(ValueError):
    pass


def get_map(north_lat,
            south_lat,
            west_lon,
            east_lon,
            resolution='appropriate',
            cross_dateline=False,
            max_filesize=None,
            ):

    # some error checking:
    if north_lat > 90:
        raise ValueError(f'latitude cannot be larger than 90. Got{north_lat}')
    # lots more to be done here


    # this is what the current GOODS API requires
    req_params = {'err_placeholder':'',
                  'NorthLat': north_lat,
                  'WestLon': west_lon,
                  'EastLon': east_lon,
                  'SouthLat': south_lat,
                  'xDateline': int(cross_dateline),
                  'resolution': 'i',
                  'submit': 'Get Map',
                  }

    query_string = urllib.parse.urlencode(req_params)
    data = query_string.encode("ascii")
    url = GOODS_URL + 'tools/GSHHS/coast_extract'

# url = url + "?" + query_string

# with urllib.request.urlopen( url ) as response:
#     response_text = response.read()
#     print( response_text )

    goods_resp = urllib.request.urlopen(url, data)

    filename = goods_resp.headers.get_filename()

    size = goods_resp.length

    if (max_filesize is not None) and size > max_filesize:
        raise ValueError(f'File is too big! Max size = {max_filesize}')

    contents = goods_resp.read().decode('utf-8')

    goods_resp.close()

    return filename, contents


