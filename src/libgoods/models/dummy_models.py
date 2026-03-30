
from .base_xsg import XSGBaseModel
from .metadata import Metadata
import datetime
import xarray as xr
import pandas as pd
import numpy as np

class DummyGlobalModel(XSGBaseModel):
    """
    A Dummy global model with all static info

    Useful for testing the API, the WebAPI, etc.
    """
    bounding_poly=((-180, -85), (-180, 85), (180, 85), (180., -85))
    metadata = Metadata(
        identifier="DUMGLOB",
        name="Dummy Global Model",
        long_name="Dummy global model with all static info for use in tests",
        html_desc="<!DOCTYPE html><html><body><p>Nothing to see here</p></body></html>",
        regional=False,
        # note -- best option for global?
        bounding_box=((-180, -85), (180, 85)),
        bounding_poly=((-180, -85), (-180, 85), (180, 85), (180, -85)),
        example_bbox=((237.1, 37.9), (237.5, 38.1)), # not sure why this is in 0->360
        start="2026-01-01T00:00:00",
        end="2026-02-24T00:00:00",
    )

    # this should get overwritten by all subclasses
    access = None

    standard_names = {
                      'eastward_sea_water_velocity': 'water_u',
                      'northward_sea_water_velocity': 'water_v',
                      'sea_water_temperature': 'water_temp',
                      'sea_water_practical_salinity': 'salinity',
                      'depth': 'depth',
                      }

    def open_ds(self):

        # manually create a dataset
        bb = self.metadata.bounding_box
        lats = np.linspace(bb[0][1], bb[1][1], 180)   # 1 degree increments
        lons = np.linspace(bb[0][0], bb[1][0], 360)  # 1 degree increments
        times = pd.date_range(self.metadata.start, self.metadata.end, freq=datetime.timedelta(hours=3))
        data_shape = (len(times), len(lats), len(lons))
        var_values = 1 + 1 * np.random.randn(*data_shape)
        self.ds = xr.Dataset(
            data_vars=dict(
                water_u=(["time", "lat", "lon"], var_values),
                water_v=(["time", "lat", "lon"], var_values),
            ),
            coords=dict(
                lon=lons,
                lat=lats,
                time=times,
            ),
            attrs=dict(description="Example dataset."),
        )
        self.actual_start = times[0].to_pydatetime()
        self.actual_end = times[-1].to_pydatetime()

    # def __init__(self, is3d=True):
    #     # add the environmental_params to metadata
    #     self.is3d = is3d
    #     self.metadata.env_params = self.env_params

class DummyRegionalModel(XSGBaseModel):
    """
    A Dummy model with all static info

    Useful for testing the API, the WebAPI, etc.
    """
    metadata = Metadata(
        identifier="DUMREG",
        name="Static Dummy Regional Model",
        long_name="Dummy regional model with all static info for use in tests",
        html_desc="<!DOCTYPE html><html><body><p>Nothing to see here</p></body></html>",
        regional=True,
        bounding_box=((236.978, 37.427), (238.319, 38.2120)),
        # note -- these are from SFBOFS, but with most of the bounding poly removed, so may be wonky
        bounding_poly=((237.824, 38.043), (237.801, 38.054), (237.797, 38.055),
                       (237.786, 38.057), (237.774, 38.057), (237.766, 38.058),
                       (237.744, 38.052), (237.844, 38.025), (237.841, 38.025),
                       (237.835, 38.028), (237.832, 38.03), (237.824, 38.043)),
        example_bbox=((237.1, 37.9), (237.5, 38.1)),
        env_params=None,
        start="2026-01-01T00:00:00",
        end="2026-02-24T00:00:00",
    )
    # this should get overwritten by all subclasses
    access = None

    standard_names = {}
