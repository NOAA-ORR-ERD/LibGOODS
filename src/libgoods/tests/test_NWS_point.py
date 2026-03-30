"""
Not fully tested, but it's something ....
"""

import datetime
from pathlib import Path

import pytest

from libgoods import NWS_point

OUTPUT = Path(__file__).parent / 'output'



EXAMPLE_DATA_DICT = {
    'location': '11NM E Pilottown LA',
    'll': (29.208333, -89.041667),
    'units': 'knots',
    'tz': -5.0,
    'times': [
        datetime.datetime(2025, 6, 3, 11, 0),
        datetime.datetime(2025, 6, 3, 12, 0),
        datetime.datetime(2025, 6, 3, 13, 0),
        datetime.datetime(2025, 6, 3, 14, 0),
        datetime.datetime(2025, 6, 3, 15, 0)
    ],
    'speeds': [10.0, 11.0, 11.0, 11.0, 11.0],
    'dirs': [90, 100, 100, 100, 100]
}

def test_download_nws_forecast():
    """
    can't test for the server being down without mocking ...

    this tests the correct case
    """
    lon, lat =  -89.041667, 29.208333
    xml_file = NWS_point.download_nws_forecast(lon, lat)

    open(OUTPUT / "example_nws.xml", 'w').write(xml_file)
    assert xml_file.startswith('<?xml version="1.0" encoding="ISO-8859-1"?>')


def test_download_nws_forecast_server_down():
    """
    Tests a bad server by breaking the url

    mocking would be better ....
    """
    good_url = NWS_point.MARINE_FORECAST_URL
    NWS_point.MARINE_FORECAST_URL = "https://marine.weather.gov/MapClick2.php"

    lon, lat =  -89.041667, 29.208333
    with pytest.raises(NWS_point.NWSServerError):
        xml_file = NWS_point.download_nws_forecast(lon, lat)  # noqa
    NWS_point.MARINE_FORECAST_URL = good_url


def test_download_nws_forecast_bad_location():
    """
    does it do the right thing if the lat-lon is bad?
    """
    lon, lat =  -52.95, 27.79  # somewhere in middle of the atlantic

    with pytest.raises(NWS_point.NWSLocationError) as err:
        xml_file = NWS_point.download_nws_forecast(lon, lat)  # noqa
    msg = err.value.message
    assert 'No Point forecast available for that location' in msg
    assert 'lat: 27.79, lon: -52.95' in msg


# @pytest.mark.skip(reason="doesn't appear to be working now ...")
def test_get_data():
    """
    tricky, as this requires hitting the server ...

    Should we run it?? Or mock it?
    """
    lon, lat =  -89.041667, 29.208333  # somewhere in the MR delta

    data = NWS_point.get_data(lon, lat)


    assert data.keys() == {'location', 'll', 'units', 'tz', 'times', 'speeds', 'dirs'}
    assert data['location'] == '11NM E Pilottown LA'
    assert data['ll'] == (29.2, -89.05)
    assert data['units'] == 'knots'

    assert data['times']  # not empty
    assert len(data['times']) == len(data['speeds']) == len(data['dirs'])


def test_get_data_bad_location():
    """
    tricky, as this requires hitting the server ...
    """

    lon, lat =  -52.95, 27.79  # somewhere in middle of the atlantic

    data = NWS_point.get_data(lon, lat)

    print(data)

    msg = data['err']
    assert 'Unable to access forecast at that location:' in msg
    assert "Lat: 27.79, Lon: -52.95" in msg

def test_format_OSSM():
    ossm_format = NWS_point.format_OSSM(EXAMPLE_DATA_DICT)

    print(ossm_format)

    for line in ossm_format:
        print(line)
        assert line[-1] == "\n"
    assert ossm_format[0].strip() == EXAMPLE_DATA_DICT['location']

    assert [float(x) for x in ossm_format[4].split(",")] ==  [3, 6, 2025, 11, 0, 10.00, 90]

    assert len(ossm_format) == 9


def test_format_JSON():
    dic = NWS_point.format_JSON(EXAMPLE_DATA_DICT)

    print(dic)

    # not a great test, but it's something
    assert dic == {
        'latitude': 29.208333,
        'longitude': -89.041667,
        'name': '11NM E Pilottown LA',
        'units':'knots',
        'tz': -5.0,
        'timeseries': [('2025-06-03T11:00:00', (10.0, 90)),
                       ('2025-06-03T12:00:00', (11.0, 100)),
                       ('2025-06-03T13:00:00', (11.0, 100)),
                       ('2025-06-03T14:00:00', (11.0, 100)),
                       ('2025-06-03T15:00:00', (11.0, 100))]
    }


def test_write_ossm():
    outfile = OUTPUT / 'example_wind.osm'
    outfile.unlink(missing_ok=True)

    ossm_data = NWS_point.format_OSSM(EXAMPLE_DATA_DICT)
    NWS_point.write_ossm(ossm_data, ofn=outfile)

    assert outfile.is_file()

    for line in open(outfile).readlines():
        print("- ", line)
    assert len(open(outfile).readlines()) == 9


