"""
COOPS TBOFS model

Not working yet with new structure
"""

import os
from ..model import Model, Metadata
from .. import temp_files_dir
from ..file_processing import roms

# fixme: we probably don't want actual HTML in there
#        but if so -- some sanitation needs to be done.
INFO_TEXT = ('NOAA NOS Operational Forecast Systems available from the '
             'Center for Operational Oceanographic Products and Services '
             '<a href="http://tidesandcurrents.noaa.gov/index.shtml" target="_blank">'
             '(COOPS)</a>. Forecast files are 36 hours and updated every 6 hours. '
             'The forecast aggregation is a "best-time series", which includes '
             'output from the latest model runs (nowcasts + latest forecast). '
             'Archived model output is available via the '
             '<a href="http://opendap.co-ops.nos.noaa.gov/netcdf/" target="_blank">CO-OPS server</a>.'
             )


class TBOFS(Model, roms):
    """
    Tampa Bay Operational Forecast system
    """

    metadata = Metadata(
        identifier="TBOFS",
        name="Tampa Bay Operational Forecast Systems",
        regional=False,
        bounding_box=((-83.172, 27.077), (-82.354, 28.031)),
        bounding_poly=((-82.8395, 27.983),
                       (-82.8558, 27.9821),
                       (-82.8705, 27.9808),
                       (-82.8915, 27.9775),
                       (-82.9116, 27.9727),
                       (-82.9312, 27.9661),
                       (-82.9503, 27.9582),
                       (-82.9689, 27.9491),
                       (-82.9868, 27.9389),
                       (-83.0036, 27.9277),
                       (-83.0202, 27.9153),
                       (-83.0317, 27.9061),
                       (-83.0435, 27.8958),
                       (-83.0562, 27.8838),
                       (-83.0687, 27.8709),
                       (-83.0808, 27.857),
                       (-83.0921, 27.8424),
                       (-83.1023, 27.8277),
                       (-83.1114, 27.8124),
                       (-83.1197, 27.7972),
                       (-83.1269, 27.7825),
                       (-83.1335, 27.7683),
                       (-83.1396, 27.7546),
                       (-83.1451, 27.7413),
                       (-83.1502, 27.7277),
                       (-83.1548, 27.7135),
                       (-83.1587, 27.6985)),
        info_text=INFO_TEXT,
        product_type='forecast',
        forecast_start="7 days in the past",
        forecast_end="3 days in the future",
        environmental_parameters=[
            "surface currents",
            "3D currents",
        ],
    )

    url = "https://opendap.co-ops.nos.noaa.gov/thredds/dodsC/TBOFS/fmrc/Aggregated_7_day_TBOFS_Fields_Forecast_best.ncd"

    var_map = {"time": "time"}
    default_filename = "tbofs.nc"

    def get_available_times(self):
        """
        returns the available times for this model as of right now

        hard-coded for now -- needs to be fixed!
        """
        return ("2022-02-17T22:00Z", "2022-02-20T22:00Z")

    def get_data(self,
                 bounds,
                 time_interval,
                 environmental_parameters,
                 cross_dateline=False,
                 max_filesize=None,
                 target_dir=None,
                 ):
        """get data"""

        if target_dir is not None:
            raise NotImplementedError(
                "TBOFS does not support setting a target directory"
            )
        self.open_nc(FileName=self.url)

        filepath = roms.get_data(self, bounds, cross_dateline, max_filesize)

        return filepath

        # url = self.url
        # var_map = self.var_map

        # model = roms(url)

        # model.get_dimensions(var_map)
        # model.subset([south_lat, west_lon, north_lat, east_lon])

        # # until I add time selection -- return last 10 time steps
        # tlen = len(model.time)

        # fn = self.default_filename
        # fp = os.path.join(temp_files_dir, fn)
        # model.write_nc(var_map, fp, t_index=[tlen - 10, tlen, 1])

        # return fn, fp
