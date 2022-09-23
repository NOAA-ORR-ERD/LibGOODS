#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module for fetching model data from the CLI."""
import sys
import warnings
from typing import List, Tuple, Optional
from pathlib import Path
from argparse import ArgumentParser

import pandas as pd
import xarray as xr
import requests
import model_catalogs as mc

from libgoods.model_fetch import (
    fetch,
    get_times,
    FetchConfig,
    DEFAULT_STANDARD_NAMES,
    get_bounds,
)

# These are just arbitrary boxes selected within the model's domain that demonstrates and offers a
# simple way to subset model output.
EXAMPLE_BBOXES = {
    "CBOFS": (-76.5, 36.75, -75.25, 37.75),
    "CIOFS": (-154.5, 58.0, -151.0, 60.0),
    "CREOFS": (-123.9, 46.1, -123.6, 46.3),
    "DBOFS": (-75.5, 38.5, -74.5, 39.25),
    "GFS-1DEG": (-85.0, 25.0, -60.0, 48.0),
    "HYCOM": (-79.10, 31.84, -68.159, 42.29),
    "LEOFS": (-83.6, 41.5, -82.6, 42.1),
    "LMHOFS": (-88, 41.57, -86, 44),
    "LOOFS": (-78.6, 43.4, -77.1, 43.7),
    "LSOFS": (-89.4, 47.0, -86.4, 47.75),
    "NGOFS2": (-91.5, 29.25, -91, 29.75),
    "NGOFS2-2DS": (-91.5, 29.25, -91, 29.75),
    "NYOFS": (-74.1, 40.49, -73.95, 40.61),
    "SFBOFS": (-122.55, 37.75, -122.4, 37.9),
    "TBOFS": (-82.9, 27.3, -82.6, 27.7),
    "WCOFS": (-122.0, 25.0, -115.0, 35.0),
    "WCOFS-2DS": (-122.0, 25.0, -115.0, 35.0),
}


def parse_bbox(
    model_name: str, val: Optional[str]
) -> Tuple[float, float, float, float]:
    """Return the bounding box parsed from the comma-delimited string.

    Parameters
    ----------
    val : str
        Comma-delimited sequence of 4 float values for (lon_min, lat_min, lon_max, lat_max)

    Returns
    -------
        tuple of 4 floats
    """
    if val is None:
        return None
    if val in ("default", "example"):
        return EXAMPLE_BBOXES[model_name]
    values = val.split(",")
    if len(values) != 4:
        raise ValueError(
            "bbox should include four numbers: lon_min,lat_min,lon_max,lat_max. bbox can also be "
            "omitted, or specified as 'example' to use the example bounding box."
        )
    return tuple(float(i) for i in values)


def parse_standard_names(value: str) -> List[str]:
    """Return a list of standard names."""
    return value.split(",")


def print_models():
    """Print each model available in model_catalogs."""
    main_cat = mc.setup()
    for item in sorted(main_cat):
        print(item)


def show_bounds(model_name: str):
    """Print the model bounds."""
    main_cat = mc.setup()
    bbox = ", ".join(f"{i:.2f}" for i in main_cat[model_name].metadata["bounding_box"])
    print(bbox)


def show_times(model_name: str):
    """Print the start/end times."""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=xr.SerializationWarning)
        times = get_times(model_name)
    print(model_name)
    for timing in times:
        start_time = times[timing][0]
        end_time = times[timing][1]
        if pd.isna(start_time):
            start_time = "undefined"
        if pd.isna(end_time):
            end_time = "undefined"
        print(f"{timing:<32} {str(start_time):<22} {str(end_time):<22}")


def show_status_all():
    """Status for all models"""
    print(f'{"model_name":<20} {"timing":<32} {"status":<6} {"start":<20} end')
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=xr.SerializationWarning)
        main_cat = mc.setup()
        for model_name in sorted(main_cat):
            _show_status(main_cat, model_name)


def show_status(model_name: str):
    """Status for model"""
    print(f'{"model_name":<20} {"timing":<32} {"status":<6} {"start":<20} end')
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=xr.SerializationWarning)
        main_cat = mc.setup()
        _show_status(main_cat, model_name)


def _show_status(main_cat, model_name):
    """Status for model"""
    yesterday = pd.Timestamp.today() - pd.Timedelta("1 day")
    cat = mc.find_availability(main_cat[model_name])
    for timing in main_cat[model_name]:
        main_cat[model_name][timing]._pick()
        urlpath = main_cat[model_name][timing]._source(yesterday=yesterday).urlpath
        if isinstance(urlpath, list):
            urlpath = urlpath[0]
        resp = requests.get(urlpath + ".das")
        if resp.status_code != 200:
            status = False
        else:
            status = True

        if status:
            start = pd.Timestamp(cat[timing].metadata["start_datetime"])
            end = pd.Timestamp(cat[timing].metadata["end_datetime"])
        else:
            start = ""
            end = ""
        print(f"{model_name:<20} {timing:<32} {str(status):<6} {str(start):<20} {end}")


def _rotate_bbox(model_name, bbox) -> Tuple[float, float, float, float]:
    """Performs checks on the bounding box relative to the model's bounds."""
    bounds = get_bounds(model_name)
    if bbox[2] < bounds[0]:
        new_bbox = list(bbox)
        if new_bbox[0] < 0:
            new_bbox[0] += 360
        if new_bbox[2] < 0:
            new_bbox[2] += 360
        return tuple(new_bbox)
    return bbox


def parse_config() -> FetchConfig:
    """Parse command line arguments into a FetchConfig object.

    Parameters
    ----------
    main : function
        A reference to the main function of the script. This is used to fill in the help output
        while parsing arguments.
    model_name : str
        Name of the model (as it appears in the catalog files).
    default_bbox : tuple of floats
        The default bounding box to use for subsetting if the user does not specify one in the
        command line arguments.
    output_dir : Path
        The output path for where to write resulting netCDF files to.
    default_timing : str
        The default model run-type to use if not specified by CLI arguments. One of "forecast",
        "nowcast", or "hindcast".
    standard_names : list of strings
        The default list of standard names to use to filter on if not specified by CLI arguments.
    default_start : datetime
        The default start time of the query to use if not specified by CLI arguments.
    default_end : datetime
        The default end time of the query to use if not specified by CLI arguments.

    Returns
    -------
    FetchConfig
        An object which contains all of the information needed by the `fetch` function for
        requesting, subsetting, and filtering a dataset.

    """
    parser = ArgumentParser(description=main.__doc__)
    parser.add_argument("model_name", nargs="?", help="Name of the model")
    parser.add_argument(
        "-t",
        "--timing",
        choices=["hindcast", "nowcast", "forecast"],
        default="hindcast",
        help="Model Timing Choice.",
    )
    parser.add_argument(
        "-s",
        "--start",
        type=pd.Timestamp,
        help="Request start time",
    )
    parser.add_argument("-e", "--end", type=pd.Timestamp, help="Request end time")
    parser.add_argument(
        "-f", "--force", action="store_true", help="Overwrite existing files"
    )
    parser.add_argument(
        "--bbox",
        default=None,
        nargs="?",
        help="Specify the bounding box. If set to 'example' an example bounding box will be used.",
    )
    parser.add_argument(
        "--surface", action="store_true", default=False, help="Fetch only surface data."
    )
    parser.add_argument(
        "-n",
        "--standard-names",
        type=parse_standard_names,
        default=DEFAULT_STANDARD_NAMES,
        help="Comma-delimited list of standard names to filter.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("./output"),
    )
    parser.add_argument(
        "-l",
        "--list-models",
        action="store_true",
        help="Print the available models and exit.",
    )
    parser.add_argument(
        "--show-bounds",
        action="store_true",
        help="Show the bounds of the model and exit.",
    )

    parser.add_argument(
        "--show-times",
        action="store_true",
        help="Show the times of the model and exit.",
    )

    parser.add_argument(
        "--show-status",
        action="store_true",
        help="Show which sources are online for the given model and exit.",
    )
    args = parser.parse_args()
    if args.list_models:
        print_models()
        sys.exit(0)

    if args.show_status:
        if args.model_name:
            show_status(args.model_name)
        else:
            show_status_all()
        sys.exit(0)

    if args.model_name is None:
        raise ValueError("model_name is required")

    if args.show_bounds:
        show_bounds(args.model_name)
        sys.exit(0)

    if args.show_times:
        show_times(args.model_name)
        sys.exit(0)

    # Sanity check on start/end time
    if args.start is None and args.end is None:
        start = pd.Timestamp("2022-06-20")
        end = pd.Timestamp("2022-06-21")
    elif args.start is None or args.end is None:
        raise ValueError("start time or end time not specified")
    else:
        start = args.start
        end = args.end
    if start >= end:
        raise ValueError("end time must be greater than start time")

    if args.output.is_dir():
        output_filename = (
            f"{args.model_name}_{args.timing}_{start:%Y%m%d}-{end:%Y%m%d}.nc"
        )
        output_pth = args.output / output_filename
    elif args.output.suffix == "":
        args.output.mkdir(parents=True)
        output_filename = (
            f"{args.model_name}_{args.timing}_{start:%Y%m%d}-{end:%Y%m%d}.nc"
        )
        output_pth = args.output / output_filename
    else:
        output_pth = args.output

    if output_pth.exists():
        if args.force:
            output_pth.unlink()
        else:
            raise FileExistsError(f"{output_pth} already exists")

    bbox = parse_bbox(args.model_name, args.bbox)
    bbox = _rotate_bbox(args.model_name, bbox)

    return FetchConfig(
        model_name=args.model_name,
        output_pth=output_pth,
        start=start,
        end=end,
        bbox=bbox,
        timing=args.timing,
        standard_names=args.standard_names,
        surface_only=args.surface,
    )


def main():
    """Fetch model output."""
    config = parse_config()
    fetch(config)


if __name__ == "__main__":
    sys.exit(main())
