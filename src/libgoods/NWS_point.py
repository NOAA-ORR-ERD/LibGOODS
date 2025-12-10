import json
from xml.etree import ElementTree

import dateutil.parser
import numpy as np
import requests

"""
Getting the point forecast from NWS.

NOTE: there is a new? API here:

https://www.weather.gov/documentation/services-web-api

It provides JSON, etc -- maybe easier than the XML?

Also -- we are hitting:

marine.weather.gov -- does it provide on-land? which we might want??

"""

MARINE_FORECAST_URL = "https://marine.weather.gov/MapClick.php"


# maybe we should be more careful, but this is step in the right direction
class NWSError(ValueError):
    """Exception raised for errors with the NWS server"""
    def __init__(self, message, nws_url):
        super().__init__(message)
        self.message = message
        self.nws_url = nws_url

    def __str__(self):
        return f"{self.message} (URL: {self.nws_url})"


class NWSServerError(NWSError):
    pass


class NWSLocationError(NWSError):
    pass


def download_nws_forecast(lon, lat, format='xml'):
    """
    Get the data from the NWS NGDF point API

    Parameters
    ----------
    lon : float | str
        longitude (decimal degrees)
    lat : float | str
        latitude (decimal degrees)

    format='xml': str
        desired format -- only xml at the moment.

    Returns
    -------
    xml with the data.

    """
    lon, lat = str(lon), str(lat)

    url_stem = MARINE_FORECAST_URL

    # nws_url = url_stem + "?lat=" + lat + "&lon=" + lon + "&FcstType=digitalDWML"
    params = {'lat': lat,
              'lon': lon,
              'FcstType': 'digitalDWML'}
    resp = requests.get(url_stem, params=params)

    if (resp.status_code == 400
        and "A point forecast is unavailable for the requested location" in resp.text):
            raise NWSLocationError("No Point forecast available for that location. "
                           f"lat: {lat}, lon: {lon}", url_stem)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        raise NWSServerError("Could not access the NWS server", url_stem)

    return resp.text


def parse_nws_xml(xml_file):
    """
    parse the xml returned by the NWS service.

    returns nws_data dict
    (see: get_data docstring for spec)
    """

    doc = ElementTree.fromstring(xml_file)

    data = doc.find("data")
    location = data.find("location")
    point = location.find("point")
    lat = point.attrib['latitude']
    lon = point.attrib['longitude']
    try:
        zone_desc = location.find("area-description").text
    except AttributeError:
        zone_desc = location.find("description").text
    except AttributeError:
        zone_desc = str(lat) + "_" + str(lon)

    time_data = data.find("time-layout")
    time_zone = time_data.attrib["time-coordinate"]

    start_times = time_data.findall("start-valid-time")

    ts = []
    for t in start_times:
        d = t.text
        try:
            part1, part2 = d.split(
                "--"
            )  # NWS uses double negative instead of plus sign (not ok with dateutil)
            d = part1 + "+" + part2
        except ValueError:
            pass
        dt = dateutil.parser.parse(d)
        ts.append(dt)

    tz = (ts[0].utcoffset().total_seconds()) / 3600  # time zone offset in hours

    params = data.find("parameters")

    wind_speed = params.findall("wind-speed")
    for wind_speed_type in wind_speed:
        if wind_speed_type.attrib["type"] == "sustained":
            wind_speed_values = wind_speed_type.findall("value")

    wspd = []
    for val in wind_speed_values:
        try:
            wspd.append(float(val.text))
        except TypeError:
            wspd.append(np.nan)

    wind_direction = params.find("direction")
    wind_direction_values = wind_direction.findall("value")

    wdir = []
    for val in wind_direction_values:
        try:
            wdir.append(int(val.text))
        except TypeError:
            wdir.append(np.nan)

    nws_data = {}
    nws_data["location"] = zone_desc
    nws_data["ll"] = (float(lat), float(lon))
    nws_data["units"] = "knots"  # this is not in XML file
    nws_data["tz"] = tz

    id = np.where(np.isfinite(wspd) * np.isfinite(wdir))[0]
    nws_data["times"] = [ts[i] for i in id]
    nws_data["speeds"] = [wspd[i] for i in id]
    nws_data["dirs"] = [wdir[i] for i in id]

    return nws_data


def get_data(lon, lat):
    """
    Get the data from the NWS NGDF point API

    Parameters
    ----------
    lon : float | str
        longitude (decimal degrees)
    lat : float | str
        latitude (decimal degrees)

    Returns
    -------
    data: dict
          keys:
              'location': str name: e.g. '11NM E Pilottown LA'
              'll': tuple of floats:  e.g. (29.208333, -89.041667)
              'units' str: e.g. 'knots'
              'tz': float -- time zone offset e.g. -5.0
              'times': list of (naive) datetime objects
              'speeds': wind speed: list of floats
              'dirs': directions -- list of numbers -- from true north


    """

    try:
        xml_file = download_nws_forecast(lon, lat)
    except NWSServerError as err:
        error_message = (f"Error: Unable to open: <br>"
                         f"{err.nws_url}"
                         f"<br>Point forecast is currently unavailable."
                         )
        return {"err": error_message}
    except NWSLocationError:
        error_message = (f"Unable to access forecast at that location:<br>"
                         f"Lat: {lat}, Lon: {lon}"
                         )
        return {"err": error_message}


    nws_data = parse_nws_xml(xml_file)

    return nws_data


def format_JSON(data):
    """
    formats the data dict into a JSON-compatible dict
    """
    webgnome = dict()

    webgnome["latitude"] = data["ll"][0]
    webgnome["longitude"] = data["ll"][1]
    webgnome["name"] = data["location"]
    webgnome["units"] = data["units"]
    webgnome["tz"] = data["tz"]

    ts = []
    for i, t in enumerate(data["times"]):
        ts.append((t.isoformat(), (data["speeds"][i], data["dirs"][i])))
    webgnome["timeseries"] = ts

    # return json.dumps(webgnome)
    return webgnome


def format_OSSM(data):
    """
    formats the data dict into a OSSM format
    list of strings.
    """
    outfile = []

    outfile.append("%s\n" % data["location"])

    outfile.append("%f, %f\n" % data["ll"])

    outfile.append("%s\n" % data["units"])
    outfile.append("%s\n" % data["tz"])
    # modern format doesn't need this :-)
    # outfile.append("0,0,0,0,0,0,0,0\n")

    for t, speed, dir in zip(data["times"], data["speeds"], data["dirs"]):
        if speed is not None:
            outfile.append("%i, %i, %i, %i, %i, %.2f, %i\n"
                            % (t.day, t.month, t.year, t.hour, t.minute, speed, dir)
                           )

    return outfile


def write_ossm(ossm_data, ofn="wind.nws"):
    """
    Is this function necessary? it's a one-liner ...
    """
    with open(ofn, "w") as outfile:
        outfile.writelines(ossm_data)
    return ofn


def error_JSON():
    error = {"status": "error", "reason": "invalid coordinates|coordinates out of bounds"}
    return json.dumps(error)
