#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""Download model data with catalog."""
import sys
import time
from typing import List, Tuple
from pathlib import Path
from argparse import ArgumentParser
from dataclasses import field, dataclass

import pandas as pd
import extract_model  # noqa

import model_catalogs as mc


class Timer:
    """A class to aid with measuring timing."""
    def __init__(self, msg=None):
        """Initializes the current time."""
        self.t0 = time.time()
        self.msg = msg

    def tick(self):
        """Update the timer start."""
        self.t0 = time.time()

    def tock(self) -> float:
        """Return elapsed time in ms."""
        return (time.time() - self.t0) * 1000.

    def __enter__(self):
        """With context."""
        self.tick()

    def __exit__(self, type, value, traceback):
        """With exit."""
        if self.msg is not None:
            print(self.msg.format(self.tock()))


STANDARD_NAMES = [
    'eastward_sea_water_velocity',
    'northward_sea_water_velocity',
    'eastward_wind',
    'northward_wind',
    'sea_water_temperature',
    'sea_water_practical_salinity',
    'sea_floor_depth',
    'longitude',
    'latitude',
]

DEFAULT_BBOX = (-154.5, 58., -151., 60.)


@dataclass
class FetchConfig:
    """Configuration data class for fetching."""
    output_pth: Path
    start: pd.Timestamp =\
        field(default_factory=lambda : pd.Timestamp('2022-06-20'))
    end: pd.Timestamp =\
        field(default_factory=lambda : pd.Timestamp('2022-06-21'))
    model_name: str = 'CIOFS'
    bbox: Tuple[float, float, float, float] = \
        field(default_factory=lambda : DEFAULT_BBOX)
    standard_names: List[str] = field(default_factory=lambda : STANDARD_NAMES)
    timing: str = 'hindcast'


def parse_bbox(val: str) -> Tuple[float, float, float, float]:
    """Return the bounding box parsed from the comma-delimited string.

    Parameters
    ----------
    val : str
        Comma-delimited sequence of 4 float values for (lon_min, lat_min, lon_max, lat_max)

    Returns
    -------
        tuple of 4 floats
    """
    values = val.split(',')
    if len(values) != 4:
        raise ValueError('bbox should include four numbers: lon_min,lat_min,lon_max,lat_max')
    return tuple(*[float(i) for i in values])


def fetch(fetch_config):
    print('Setting up source catalog')
    with Timer('\tSource catalog generated in {:.1f} ms'):
        source_catalog = mc.setup_source_catalog()

    print('Generating catalog specific for CIOFS hindcast')
    with Timer('\tSpecific catalog generated in {:.1f} ms'):
        catalog = mc.add_url_path(source_catalog[fetch_config.model_name],
                                  timing=fetch_config.timing,
                                  start_date=fetch_config.start,
                                  end_date=fetch_config.end)
    print('Getting xarray dataset for model data')
    with Timer('\tCreated dask-based xarray dataset in {:.1f} ms'):
        ds = catalog[fetch_config.model_name].to_dask()
    print('Subsetting data')
    with Timer('\tSubsetted dataset in {:.1f} ms'):
        ds_ss = (
            ds
            .em.filter(STANDARD_NAMES)
            .cf.sel(T=slice(fetch_config.start, fetch_config.end))
            .em.sub_grid(bbox=fetch_config.bbox)
        )
        # TODO: This is going to get moved into model_catalogs, but some models from CO-OPS contain
        #   a global attribute that originates from NETCDF3. However when xarray attempts to write
        #   this special global attribute to disk, the netCDF-C library will throw an exception. See
        #   https://github.com/pydata/xarray/issues/2822 for details.
        if '_NCProperties' in ds_ss.attrs:
            del ds_ss.attrs['_NCProperties']
    print(f'Writing netCDF data to {fetch_config.output_pth}. This may take a long time, '
          '~20-minutes per 24h period is an estmate.')
    with Timer('\tWrote output to disk in {:.1f} ms'):
        ds_ss.to_netcdf(fetch_config.output_pth)
    print('Complete')


def main():
    """Fetch CIOFS Model Data."""
    parser = ArgumentParser(description=main.__doc__)
    parser.add_argument('-t',
                        '--timing',
                        choices=['hindcast', 'nowcast', 'forecast'],
                        default=FetchConfig.timing,
                        help='Model Timing Choice.')
    parser.add_argument('-s', '--start', type=pd.Timestamp, help='Request start time')
    parser.add_argument('-e', '--end', type=pd.Timestamp, help='Request end time')
    parser.add_argument('-f', '--force', action='store_true', help='Overwrite existing files')
    parser.add_argument('--bbox',
                        type=parse_bbox,
                        default=DEFAULT_BBOX,
                        help='Specify the bounding box')
    args = parser.parse_args()

    # Sanity check on start/end time
    if args.start is None and args.end is None:
        start = pd.Timestamp('2022-06-20')
        end = pd.Timestamp('2022-06-21')
    elif args.start is None or args.end is None:
        raise ValueError('start time or end time not specified')
    else:
        start = args.start
        end = args.end
    if start >= end:
        raise ValueError('end time must be greater than start time')

    # Check output
    output_dir = Path(__file__).parent / 'output'
    if not output_dir.exists():
        output_dir.mkdir()
    output_filename = (
        f'{FetchConfig.model_name}_{args.timing}_{start:%Y%m%d}-{end:%Y%m%d}.nc'
    )
    output_pth = output_dir / output_filename
    if output_pth.exists():
        if args.force:
            output_pth.unlink()
        else:
            raise FileExistsError(f'{output_pth} already exists')

    config = FetchConfig(
        start=start,
        end=end,
        output_pth=output_pth,
        bbox=args.bbox,
        timing=args.timing,
    )
    fetch(config)
    return 0


if __name__ == '__main__':
    sys.exit(main())
