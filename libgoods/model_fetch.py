#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A module containing code for fetching content from models."""
import time
import warnings
from typing import List, Tuple, Mapping, Optional
from pathlib import Path
from dataclasses import field, dataclass

import numpy as np
import pandas as pd
import xarray as xr
import requests
import model_catalogs as mc
from extract_model import utils as em_utils

# from libgoods.performance import Timer

DEFAULT_STANDARD_NAMES = [
    "eastward_sea_water_velocity",
    "northward_sea_water_velocity",
    "eastward_wind",
    "northward_wind",
    "sea_water_temperature",
    "sea_water_practical_salinity",
    "sea_floor_depth",
]


@dataclass
class FetchConfig:
    """Configuration data class for fetching."""

    model_name: str
    output_pth: Path
    start: pd.Timestamp
    end: pd.Timestamp
    bbox: Optional[Tuple[float, float, float, float]]
    timing: str
    standard_names: List[str] = field(default_factory=lambda: DEFAULT_STANDARD_NAMES)
    surface_only: bool = False


def select_surface(ds: xr.Dataset) -> xr.Dataset:
    """Return a dataset that is reduced to only the surface layer."""
    model_guess = em_utils.guess_model_type(ds)
    # SELFE uses a hybrid sigma coordinate system for the vertical coordinates,
    # but cf_xarray misinterprets it as being the z variable. So, we check SELFE
    # first, before trying to use cf_xarray
    if model_guess == "SELFE":
        return ds.isel(nv=-1)
    elif model_guess == "FVCOM":
        vertical_dims = set()
        for varname in ds.cf.axes["Z"]:
            vertical_dim = ds[varname].dims[0]
            vertical_dims.add(vertical_dim)
        sel_kwargs = {vdim: 0 for vdim in vertical_dims}
        return ds.isel(**sel_kwargs)
    elif all([ds[zaxis].ndim < 2 for zaxis in ds.cf.axes["Z"]]):
        return ds.cf.sel(Z=0, method="nearest")
    raise ValueError("Can't decode vertical coordinates.")


def get_times(model_name: str) -> Mapping[str, pd.Timestamp]:
    """Return a mapping of a source to the start and end datetimes."""
    main_cat = mc.setup()
    cat = mc.find_availability(main_cat[model_name])
    timing_date_map = {}
    for timing in cat:
        timing_date_map[timing] = (
            pd.Timestamp(cat[timing].metadata["start_datetime"]),
            pd.Timestamp(cat[timing].metadata["end_datetime"]),
        )
    return timing_date_map


def get_source_online_status(model_name: str) -> Mapping[str, bool]:
    """Return a mapping of source to a boolean indicating if the source is available."""
    yesterday = pd.Timestamp.today() - pd.Timedelta("1 day")
    main_cat = mc.setup()
    statuses = {}
    for timing in main_cat[model_name]:
        main_cat[model_name][timing]._pick()
        urlpath = main_cat[model_name][timing]._source(yesterday=yesterday).urlpath
        if isinstance(urlpath, list):
            urlpath = urlpath[0]
        resp = requests.get(urlpath + ".das")
        if resp.status_code != 200:
            statuses[timing] = False
        else:
            statuses[timing] = True
    return statuses


def get_bounds(model_name: str) -> Tuple[float, float, float, float]:
    """Returns the geospatial extents for the model."""
    main_cat = mc.setup()
    return main_cat[model_name].metadata["bounding_box"]


def is_monotonic(data: np.array) -> bool:
    """Return true if the array is monotonically increasing or decreasing."""
    increasing = np.all(data[1:] >= data[:-1])
    decreasing = np.all(data[1:] <= data[:-1])
    return increasing or decreasing


def is_coordinate_variable(ds: xr.Dataset, varname: str) -> bool:
    """Return True if the variable is a coordinate variable."""
    return ds[varname].dims == (varname,)


def rotate_longitude(ds: xr.Dataset) -> xr.Dataset:
    """Returns a dataset in which the longitude coordinate is rotated to [-180, 180] values."""
    new_vars = {}
    for varname in ds.filter_by_attrs(standard_name="longitude").variables:
        if "standard_name" not in ds[varname].attrs:
            continue
        if ds[varname].attrs["standard_name"] != "longitude":
            continue
        lon_data = ds[varname][:].to_numpy()
        rotated_data = np.copy(lon_data)
        rotated_data[rotated_data > 180] -= 360
        if is_coordinate_variable(ds, varname) and not is_monotonic(rotated_data):
            warnings.warn(
                "Longitude can not be rotated because the rotated data are not monotonic."
            )
        else:
            xvar = xr.DataArray(
                rotated_data, dims=ds[varname].dims, attrs=ds[varname].attrs
            )
            new_vars[varname] = xvar
    if len(new_vars) > 0:
        ds = ds.assign(new_vars)
    return ds


def rotate_bbox(model_name: str, bbox: em_utils.BBoxType) -> em_utils.BBoxType:
    """Performs checks on the bounding box relative to the model's bounds.

    This function checks the bounding box relative to the domain of the region.
    If the bounding box uses [-180, 180] and the model uses [0, 360] the
    bounding box elements are shifted into the domain.
    """
    bounds = get_bounds(model_name)
    if bbox[2] < bounds[0]:
        new_bbox = list(bbox)
        if new_bbox[0] < 0:
            new_bbox[0] += 360
        if new_bbox[2] < 0:
            new_bbox[2] += 360
        return tuple(new_bbox)
    return bbox


def _check_axis(ds: xr.Dataset, axis: str) -> bool:
    """Return true if the axis has a size greater than 1."""
    if axis not in ds.cf.axes:
        return True
    for varname in ds.cf.axes[axis]:
        if ds[varname].dims == (varname,):
            if ds.dims[varname] > 0:
                return True
    return False


def has_horizontal_data(ds: xr.Dataset) -> bool:
    """Return true if the horizontal size of the dataset is 0."""
    horizontal_axes = ["X", "Y"]
    for axis in horizontal_axes:
        if _check_axis(ds, axis):
            return True
    return False


def fetch(fetch_config: FetchConfig):
    """Downloads and subsets the model data.

    Parameters
    ----------
    fetch_config : FetchConfig
        The configuration object which contains the model name, timing, start/end dates of the
        request, etc.
    """
    print("Setting up source catalog")
    with Timer("\tSource catalog generated in {}"):
        main_cat = mc.setup()

    print(
        f"Generating catalog specific for {fetch_config.model_name} {fetch_config.timing}"
    )
    with Timer("\tSpecific catalog generated in {}"):
        source = mc.select_date_range(
            main_cat[fetch_config.model_name],
            start_date=fetch_config.start,
            end_date=fetch_config.end,
            timing=fetch_config.timing,
        )

    print("Getting xarray dataset for model data")
    with Timer("\tCreated dask-based xarray dataset in {}"):
        ds = source.to_dask()

    if fetch_config.surface_only:
        print("Selecting only surface data.")
        with Timer("\tIndexed surface data in {}"):
            ds = select_surface(ds)

    print("Subsetting data")
    with Timer("\tSubsetted dataset in {}"):
        ds_ss = ds.em.filter(fetch_config.standard_names)
        if fetch_config.bbox is not None:
            ds_ss = ds_ss.em.sub_grid(bbox=fetch_config.bbox, naive=True, preload=True)
        print(
            f"Estimated size of uncompressed dataset: {ds_ss.nbytes / 1024 / 1024:.2f} MiB"
        )

        if main_cat[fetch_config.model_name].metadata["bounding_box"][2] > 180:
            ds_ss = rotate_longitude(ds_ss)

        if not has_horizontal_data(ds_ss):
            raise ValueError("Subsetting produced no valid data to write to disk.")
    print(f"Writing netCDF data to {fetch_config.output_pth}.")
    with Timer("\tWrote output to disk in {}"):
        ds_ss.to_netcdf(fetch_config.output_pth)
    print("Complete")
