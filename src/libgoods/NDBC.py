import urllib
from weathertools import metdata
import os
import numpy as np
from netCDF4 import Dataset, num2date
import datetime


def urldata2file(station, tfn):
    """
    Navigate to url for input NDBC station and parse text

    """
    # NDBC_url = 'http://www.ndbc.noaa.gov/data/5day2/' + station + '_5day.txt' #add check this exists
    NDBC_url = "http://www.ndbc.noaa.gov/data/realtime2/" + station + ".txt"
    f = urllib.urlopen(NDBC_url)
    firstline = f.readline()
    f.close()
    if firstline.lower().startswith("<!doctype html"):
        error_msg = (
            "Error reading from url: "
            + NDBC_url
            + ". Either the station does not exist or there is no recent data."
        )
        return error_msg
    else:
        f = urllib.urlopen(NDBC_url)
        file_out = open(tfn, "w")
        file_out.writelines(f)
        file_out.close()
        return None


def convert(station, tz, time_period, tfn):
    """

    Use Chris Barker's weathertools to convert from NDBC text file to osm format

    """
    err = urldata2file(station.upper(), tfn)

    if err is not None:
        return err
    else:
        Data = metdata.MetData(tfn)
        sdate = Data.Times[-1] - datetime.timedelta(days=int(time_period))
        Data.TruncateTimeSeries(sdate=sdate)
        os.remove(tfn)
        tz_hrs = abs(int(tz))
        Data.ChangeTZ(tz_hrs, tz)
        Data.SaveAsOSSMWind(tfn, units="knots")
        return " "


def plot(station, tz, time_period, tfn):
    err = urldata2file(station.upper(), tfn)

    if err is not None:
        return err
    else:
        import matplotlib as mpl

        mpl.use("Agg")
        import matplotlib.pyplot as plt

        Data = metdata.MetData(tfn)
        sdate = Data.Times[-1] - datetime.timedelta(days=int(time_period))
        Data.TruncateTimeSeries(sdate=sdate)
        os.remove(tfn)
        tz_hrs = abs(int(tz))
        Data.ChangeTZ(tz_hrs, tz)
        times = Data.Times
        data = Data[("WindSpeed", "WindDirection")]
        speeds = data[:, 0]
        directions = (data[:, 1] + 90) * -1
        wind_units = Data.Units["WindSpeed"]
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

        # Q = axes.quiver(times, y, speeds, v, angles=directions.reshape((-1,1)), **props)
        axes.quiver(times, y, u, v, **props)
        axes.axhline(y=0, linewidth=1, color="r")

        axes.set_xlim(times[0], times[-1])
        axes.yaxis.set_major_locator(mpl.ticker.NullLocator())

        somedays = mpl.dates.DayLocator(bymonthday=[10, 20, 30])
        alldays = mpl.dates.DayLocator()
        allhours = mpl.dates.HourLocator()
        somehours = mpl.dates.HourLocator(byhour=[0, 6, 12, 18])
        weekFormatter = mpl.dates.DateFormatter("%b %d")  # Eg, Jan 12
        dayFormatter = mpl.dates.DateFormatter("%b %d %H:00")  # Eg, Jan 12 12:00
        if int(time_period) > 10:
            axes.xaxis.set_major_locator(somedays)
            axes.xaxis.set_minor_locator(alldays)
            axes.xaxis.set_major_formatter(weekFormatter)
        elif int(time_period) > 1:
            axes.xaxis.set_major_locator(alldays)
            axes.xaxis.set_minor_locator(allhours)
            axes.xaxis.set_major_formatter(weekFormatter)
        else:
            axes.xaxis.set_major_locator(somehours)
            axes.xaxis.set_major_formatter(dayFormatter)
            axes.xaxis.set_minor_locator(allhours)
        plt.xticks(rotation=45)

        # scale
        offset = 0.085 * int(time_period)
        yl = plt.ylim()
        axes.quiver(
            times[0] - offset / 2.0, 0, 0, 10, units="y", scale=props["scale"], clip_on=False
        )
        axes.text(times[0] - offset, -0.01, "10" + wind_units)
        plt.ylim(yl)

        plt.savefig(tfn, format="png")
        plt.close(fig)

        return " "


def get_historical(stn_id, tfn):
    try:
        server_url = (
            "http://dods.ndbc.noaa.gov/thredds/dodsC/data/stdmet/"
            + str(stn_id).lower()
            + "/"
            + str(stn_id).lower()
            + ".ncml"
        )

        nc = Dataset(server_url)
        t_obj = nc.variables["time"]
        ts = num2date(t_obj[:], t_obj.units)

        lat = nc.variables["latitude"][:]
        lon = nc.variables["longitude"][:]
        wdir_obj = nc.variables["wind_dir"]
        wspd_obj = nc.variables["wind_spd"]

        # add data to metdata object manually (no reader for this yet)
        data = metdata.MetData(TimeZone="UTC")
        data.Times = list(ts)
        data.Fields = {"WindDirection": 0, "WindSpeed": 1}
        data.LatLong = (lat, lon)
        if wspd_obj.units == "meters/second":
            wspd_un = "m/s"
        else:
            wspd_un = wspd_obj.units
        data.Units = {"WindDirection": wdir_obj.units, "WindSpeed": wspd_un}

        l = len(wdir_obj)
        wspd = wspd_obj[0 : l - 1].data
        wspd = (wspd > 98).choose(wspd, np.nan)
        wdir = wdir_obj[0 : l - 1].data
        wdir = (wdir > 360).choose(wdir, np.nan)

        data.DataArray = np.concatenate((wdir, wspd), axis=1).squeeze()
        data.SaveAsOSSMWind(tfn, units="knots")

        valid = np.where(np.logical_and(np.isfinite(wdir), np.isfinite(wspd)))[0]

        sd = ts[valid[0]].strftime("%b%Y")
        ed = ts[valid[-1]].strftime("%b%Y")

        return " ", [sd, ed]
    except:
        return "Error: Unable to access historical data for this station from " + server_url, [
            "",
            "",
        ]
