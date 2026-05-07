import datetime
import os
import requests
import tempfile
import numpy as np
from netCDF4 import Dataset, num2date
from . import metdata


def get_recent_data_from_url(station, tz='00', number_days_ago=45):
    """
    This function retrieves recent NDBC data from a URL for a specified station,
    and uses metdata.MetData to truncate the time series to the specifed number of days ago,
    and change the timezone if desired (from UTC).

    A station list can be found here:
    https://www.ndbc.noaa.gov/to_station.shtml

    For WMO stations they are in the form &&### where && designates region - such as:
        32 - the Pacific off the coast of South America,
        41 - the Atlantic off of the southeast U.S. coast,
        42 - the Gulf of America,
        44 - the Atlantic Ocean north of North Carolina,
        45 - the Great Lakes,
        46 - the U.S. coastal Pacific Ocean,
        51 - the Hawaiian Islands,
        52 - Guam.

    C-MAN Stations are alphanumeric AAAS#
        S# is the first alphabetic letter for the state its in followed by an ascending number
        AAA is some sort of descriptor
        e.g., GDIL1 for Grande Isle, LA

    Parameters
    ----------
    station : str
        The NDBC station identifier or URL used to fetch the data.
    tz : str
        The timezone offset string (e.g., '-07') to apply for time conversion.
    number_days_ago : int or str
        The number of days before preent  to keep in the time series;
        data is truncated to the latest `time_period` days.
        Max is 45 days ago for this source


    Returns
    -------
    metdata.MetData
        A populated object containing time series for 'WindDirection' (degrees)
        and 'WindSpeed' (m/s or original units), along with available station metadata

    """


    NDBC_url = "http://www.ndbc.noaa.gov/data/realtime2/" + station + ".txt"
    r = requests.get(NDBC_url)

    if r.status_code == 404:
        error_msg = (
            "Error reading from url: "
            + NDBC_url
            + ". Either the station does not exist or there is no recent data."
        )
        raise ValueError(error_msg)

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmpf:
        tmpf.write(r.text)
        data = metdata.MetData(tmpf.name) # TODO: MetData object should be refactored to be able to take data directly

    sdate = data.Times[-1] - datetime.timedelta(days=int(number_days_ago))
    data.TruncateTimeSeries(sdate=sdate)
    data.ChangeTZ(int(tz), tz)
    data.Name = station

    return data


def write_osm_file(data,  out_file_name=None):
    """
    Writes NDBC recent station data into the OSM wind format using the metdata module.

    This function fetches NDBC data from a URL for a specified station, processes it using
    metdata.MetData, truncates the time series to the specifed number of days ago,
    changes the timezone, and saves the resulting wind data to a file.

    Parameters
    ----------
    data : metdata.Metdata object

    tz : str
        The timezone offset string (e.g., '-07') to apply for time conversion.

    out_file_name : str
        The file path for the output OSM wind format file. If None the
        Name attribute from the Data object is used

    """

    if out_file_name is None:
        out_file_name = data.Name + '.osm'
    data.SaveAsOSSMWind(out_file_name, units="knots")


def get_historical_data_TDS(station, year=None, tz='00'):
    """
    Retrieve standard meteorological data from the NDBC THREDDS Data Server (TDS).

    This function accesses historical wind direction and wind speed data for a specified
    NDBC station, converting the netCDF output into a `metdata.MetData` object.
    It removes missing data points (wind speed > 98, wind direction > 360) with NaNs.

    Data availability can be determined from the NDBC TDS catalog:
    https://dods.ndbc.noaa.gov/thredds/catalog/data/stdmet/catalog.html

    Parameters
    ----------
    station : str
        The NDBC station ID (e.g., '41000' or 'DESW1'). Used to construct the URL.
    year : int, optional
        The specific year of data to retrieve. If provided, the function accesses
        a year-specific netCDF file (e.g., 'stationhYYYY.nc'). If None (default), it
        attempts to load the aggregated data file ('station.ncml').
    tz : str or int, optional
        The target timezone offset (e.g., '-07') to convert the data to.
        The source data is assumed to be in UTC. Default is '00'.


    Returns
    -------
    metdata.MetData
        A populated object containing time series for 'WindDirection' (degrees)
        and 'WindSpeed' (m/s or original units), along with available station metadata


    """

    try:
        server_url_base = "http://dods.ndbc.noaa.gov/thredds/dodsC/data/stdmet/" + str(station).lower() + "/"
        if year is not None:
            server_url = server_url_base + str(station).lower()  + "h" + str(year) + ".nc"
        else:
            server_url = server_url_base + str(station).lower()  + ".ncml"

        nc = Dataset(server_url)

    except FileNotFoundError:
        error_msg = "Error: Unable to access historical data for this station from " + server_url
        raise ValueError(error_msg)


    t_obj = nc.variables["time"]
    ts = num2date(t_obj[:], t_obj.units)

    lat = nc.variables["latitude"][:]
    lon = nc.variables["longitude"][:]
    wdir_obj = nc.variables["wind_dir"]
    wspd_obj = nc.variables["wind_spd"]

    # add data to metdata object manually (no reader for this yet)
    data = metdata.MetData(TimeZone="UTC", TimeZoneOffset=0)
    data.Times = list(ts)
    data.Fields = {"WindDirection": 0, "WindSpeed": 1}
    data.LatLong = (lat, lon)
    if wspd_obj.units == "meters/second":
        wspd_un = "m/s"
    else:
        wspd_un = wspd_obj.units
    data.Units = {"WindDirection": wdir_obj.units, "WindSpeed": wspd_un}

    wspd = wspd_obj[:]
    wspd = (wspd > 98).choose(wspd, np.nan)
    wdir = wdir_obj[:]
    wdir = (wdir > 360).choose(wdir, np.nan)

    data.DataArray = np.concatenate((wdir, wspd), axis=1).squeeze()
    data.ChangeTZ(int(tz), tz)

    valid = np.where(np.logical_and(np.isfinite(wdir), np.isfinite(wspd)))[0]

    sd = ts[valid[0]].strftime("%b%Y")
    ed = ts[valid[-1]].strftime("%b%Y")

    data.Name = station + "_" + sd + '_to_' + ed


    return data

def plot(data):

    try:
        import matplotlib as mpl
        mpl.use("Agg") # this was for creating png on server
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError('matplotlib required for plotting')


    times = data.Times
    speeds = data["WindSpeed"][:, 0]
    directions = (data["WindDirection"][:, 0] + 90) * -1
    wind_units = data.Units["WindSpeed"]
    # make plot
    fig = plt.figure()
    axes = fig.add_subplot(2, 1, 1)

    props = {
        "units": "y",
        "width": 0.001,
        "headwidth": 0,
        "headlength": 0,
        "headaxislength": 0,
        "scale": 250,
    }

    times = mpl.dates.date2num(times)
    dir_rad = directions / 180.0 * np.pi
    u = np.cos(dir_rad) * speeds
    v = np.sin(dir_rad) * speeds
    y = np.zeros_like(speeds)

    time_period_days = times[-1] - times[0]
    if time_period_days > 60:
        times=times[::10]
        u = u[::10]
        v = v[::10]
        y = y[::10]

    # Q = axes.quiver(times, y, speeds, v, angles=directions.reshape((-1,1)), **props)
    axes.quiver(times, y, u, v, **props)
    axes.axhline(y=0, linewidth=1, color="r")

    axes.set_xlim(times[0], times[-1])
    axes.yaxis.set_major_locator(mpl.ticker.NullLocator())

    months = mpl.dates.MonthLocator()
    somedays = mpl.dates.DayLocator(bymonthday=[10, 20, 30])
    alldays = mpl.dates.DayLocator()
    allhours = mpl.dates.HourLocator()
    somehours = mpl.dates.HourLocator(byhour=[0, 6, 12, 18])
    weekFormatter = mpl.dates.DateFormatter("%b %d")  # Eg, Jan 12
    dayFormatter = mpl.dates.DateFormatter("%b %d %H:00")  # Eg, Jan 12 12:00
    monthFormatter = mpl.dates.DateFormatter("%m/%d/%y")

    if  int(time_period_days) > 60:
        axes.xaxis.set_major_locator(months)
        # axes.xaxis.set_minor_locator(somedays)
        axes.xaxis.set_major_formatter(monthFormatter)
    elif int(time_period_days) > 10:
        axes.xaxis.set_major_locator(somedays)
        axes.xaxis.set_minor_locator(alldays)
        axes.xaxis.set_major_formatter(weekFormatter)
    elif int(time_period_days) > 1:
        axes.xaxis.set_major_locator(alldays)
        axes.xaxis.set_minor_locator(allhours)
        axes.xaxis.set_major_formatter(weekFormatter)
    else:
        axes.xaxis.set_major_locator(somehours)
        axes.xaxis.set_major_formatter(dayFormatter)
        axes.xaxis.set_minor_locator(allhours)
    plt.xticks(rotation=45)

    # scale
    offset = 0.085 * int(time_period_days)
    yl = plt.ylim()
    axes.quiver(
        times[0] - offset / 2.0, 0, 0, 10, units="y", scale=props["scale"], clip_on=False
    )
    axes.text(times[0] - offset, -0.01, "10" + wind_units)
    plt.ylim(yl)

    out_file_name = data.Name + '.png'
    plt.savefig(out_file_name, format="png")
    plt.close(fig)


