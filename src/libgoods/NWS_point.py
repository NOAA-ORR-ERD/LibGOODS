import json
import urllib
from xml.etree import ElementTree

import dateutil.parser
import numpy as np

#TODO -- could make use of some of the Weathertools module

def get_data(lon,lat):

    nws_data = {}

    url_stem = 'https://marine.weather.gov/MapClick.php'
    nws_url = url_stem + '?lat=' + lat + \
        '&lon=' + lon + '&FcstType=digitalDWML'
    try:
        xml_file = urllib.request.urlopen(nws_url)
    except:
        nws_data['err'] = 'Error: Unable to open: <br>' + url_stem + '?lat=' + lat + '&lon=' + lon \
            + '<br>Point forecast may be unavailable for this location.'
        return nws_data

    try:
        tree = ElementTree.parse(xml_file)
    except:
        nws_data['err'] = 'Error: Unable to open: <br>' + url_stem + '?lat=' + lat + '&lon=' + lon \
            + '<br>Point forecast may be unavailable for this location.'
        return nws_data

    doc = tree.getroot()

    data = doc.find('data')
    location = data.find('location')
    try:
        zone_desc = location.find('area-description').text
    except AttributeError:
        zone_desc = location.find('description').text
    except AttributeError:
        zone_desc = str(lat) + '_' + str(lon)

    time_data = data.find('time-layout')
    time_zone = time_data.attrib['time-coordinate']

    start_times = time_data.findall('start-valid-time')

    ts = []
    for t in start_times:
        d = t.text
        try:
            part1,part2 = d.split('--') #NWS uses double negative instead of plus sign (not ok with dateutil)
            d = part1 + '+' + part2
        except ValueError:
            pass
        dt = dateutil.parser.parse(d)
        ts.append(dt)

    tz = (ts[0].utcoffset().total_seconds())/3600 #time zone offset in hours

    params = data.find('parameters')

    wind_speed = params.findall('wind-speed')
    for wind_speed_type in wind_speed:
        if wind_speed_type.attrib['type'] == 'sustained':
            wind_speed_values = wind_speed_type.findall('value')

    wspd = []
    for val in wind_speed_values:
        try:
            wspd.append(float(val.text))
        except TypeError:
            wspd.append(np.nan)

    wind_direction = params.find('direction')
    wind_direction_values = wind_direction.findall('value')

    wdir = []
    for val in wind_direction_values:
        try:
            wdir.append(int(val.text))
        except TypeError:
            wdir.append(np.nan)


    nws_data['location'] = zone_desc
    nws_data['ll'] = (float(lat),float(lon))
    nws_data['units'] = 'knots' #this is not in XML file
    nws_data['tz'] = tz

    id = np.where(np.isfinite(wspd) * np.isfinite(wdir))[0]
    nws_data['times'] = [ts[i] for i in id]
    nws_data['speeds'] = [wspd[i] for i in id]
    nws_data['dirs'] = [wdir[i] for i in id]


    return nws_data


def format_JSON(data):

    webgnome = dict()

    webgnome['latitude'] = data['ll'][0]
    webgnome['longitude'] = data['ll'][1]
    webgnome['name'] = data['location']
    webgnome['units'] = data['units']

    ts = []
    for i,t in enumerate(data['times']):
        ts.append((t.isoformat(),(data['speeds'][i],data['dirs'][i])))
    webgnome['timeseries'] = ts

    return json.dumps(webgnome)


def format_OSSM(data):

    outfile = []

    outfile.append("%s\n"%data['location'])

    outfile.append("%f, %f\n"%data['ll'])

    outfile.append("%s\n"%data['units'])
    outfile.append("%s\n"%data['tz'])
    outfile.append("0,0,0,0,0,0,0,0\n")

    for t, speed, dir in zip(data['times'],data['speeds'],data['dirs']):
        if speed is not None:
            outfile.append("%i, %i, %i, %i, %i, "%(t.day, t.month, t.year, t.hour, t.minute))
            outfile.append("%.2f, %i\n"%(speed, dir))

    return outfile

def write_ossm(ossm_data,ofn='wind.nws'):

    f = open(ofn,'w')
    f.writelines([l for l in ossm_data])
    f.close()



def error_JSON():
    error = {
        "status": "error",
        "reason": "invalid coordinates|coordinates out of bounds"
        }
    return json.dumps(error)
