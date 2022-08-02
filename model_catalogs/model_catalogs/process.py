"""
This file contains all information for transforming the Datasets.
"""
from typing import Optional

import cf_xarray  # noqa
import numpy as np
import xarray as xr

from intake.source.derived import GenericTransform


class DatasetTransform(GenericTransform):
    """Transform where the input and output are both Dask-compatible Datasets

    This derives from GenericTransform, and you must supply ``transform`` and
    any ``transform_kwargs``.
    """

    input_container = "xarray"
    container = "xarray"
    optional_params = {}
    _ds = None

    def to_dask(self):
        """Makes it so can read in model output."""
        if self._ds is None:
            self._pick()
            # import pandas as pd
            kwargs = self._params["transform_kwargs"]
            if 'yesterday' in kwargs:
                self._source = self._source(yesterday=kwargs['yesterday'])
                kwargs.pop('yesterday')
            # import pdb; pdb.set_trace()
            # kwargs["metadata"] = self.metadata
            self._ds = self._transform(
                self._source.to_dask(),
                metadata=self.metadata,
                # **kwargs,
            )

        return self._ds

    def read(self):
        """Same here."""
        return self.to_dask()


def add_attributes(ds, metadata: Optional[dict] = None):
# def add_attributes(ds, axis, standard_names, metadata: Optional[dict] = None):
    """Update Dataset metadata.

    Using supplied axis variable names and variable name mapping to associated
    standard names (from CF conventions), update the Dataset metadata.
    """
    # set standard_names for all variables
    if metadata is not None and "standard_names" in metadata:
        for stan_name, var_names in metadata["standard_names"].items():
            if not isinstance(var_names, list):
                var_names = [var_names]
            for var_name in var_names:
                if var_name in ds.data_vars:
                    ds[var_name].attrs["standard_name"] = stan_name

    # # Run code to find vertical coordinates
    # try:
    #     # create name mapping
    #     snames = ['ocean_s_coordinate_g1', 'ocean_s_coordinate_g2', 'ocean_sigma_coordinate']
    #     s_vars = [standard_names[sname] for sname in snames if sname in standard_names][0]
    #     z_vars = axis['Z']
    #     outnames = {s_var: z_var for s_var, z_var in zip(s_vars, z_vars)}
    #     ds.cf.decode_vertical_coords(outnames=outnames)
    # except Exception:
    #     pass

    if metadata is not None and "coords" in metadata:
        ds = ds.assign_coords({k: ds[k] for k in metadata["coords"]})

    # set axis attributes (time, lon, lat, z potentially)
    if metadata is not None and "axis" in metadata:
        for ax_name, var_names in metadata["axis"].items():
            if not isinstance(var_names, list):
                var_names = [var_names]
            for var_name in var_names:
                # var_name needs to exist
                # if ax_name == 'X':
                #     import pdb; pdb.set_trace()

                if var_name in ds.dims:
                    # var_name needs to be a coord to have attributes
                    if var_name not in ds.coords:
                        ds[var_name] = (
                            var_name,
                            np.arange(ds.sizes[var_name]),
                            {"axis": ax_name},
                        )
                    else:
                        ds[var_name].attrs["axis"] = ax_name

    # this won't run for e.g. GFS which has multiple time variables
    # but also doesn't need to have the calendar updated
    try:
        attrs = ds[ds.cf["T"].name].attrs
        if ("calendar" in attrs) and (attrs["calendar"] == "gregorian_proleptic"):
            attrs["calendar"] = "proleptic_gregorian"
            ds[ds.cf["T"].name].attrs = attrs
    except KeyError:
        pass

    # decode times if times are floats.
    # Some datasets like GFS have multiple time coordinates for different phenomena like
    # precipitation accumulation vs winds vs surface albedo average.
    if "T" in metadata["axis"] and isinstance(metadata["axis"]["T"], list) and len(metadata["axis"]["T"]) > 1:
        for time_var in metadata["axis"]["T"]:
            if ds[time_var].dtype == "float64":
                ds = xr.decode_cf(ds, decode_times=True)
                break
    elif ds.cf["T"].dtype == "float64":
        ds = xr.decode_cf(ds, decode_times=True)

    # This is an internal attribute used by netCDF which xarray doesn't know or care about, but can
    # be returned from THREDDS.
    if "_NCProperties" in ds.attrs:
        del ds.attrs["_NCProperties"]

    return ds
