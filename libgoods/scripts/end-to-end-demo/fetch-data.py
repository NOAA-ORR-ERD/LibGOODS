#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Example command script to fetch LOOFS data."""
import sys
import argparse
from pathlib import Path
from dataclasses import field, dataclass
import extract_model  # noqa

import pandas as pd

import model_catalogs as mc

STANDARD_NAMES = [
    'eastward_sea_water_velocity',
    'northward_sea_water_velocity',
    'sea_water_temperature',
    'sea_water_practical_salinity',
    'sea_floor_depth'
]


@dataclass
class ModelConfig:
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    model_name: str = 'LOOFS'
    lon_range: list = field(default_factory=lambda: [-78.8, -77.5])
    lat_range: list = field(default_factory=lambda: [43.5,  43.8])
    timing: str = 'forecast'
    standard_names: list = field(default_factory=lambda: STANDARD_NAMES)


def fetch_data(config: ModelConfig, output_dir: Path) -> Path:
    """Fetch data for a given model config, save to output dir as netcdf."""
    bbox = [
        config.lon_range[0],
        config.lat_range[0],
        config.lon_range[1],
        config.lat_range[1]
    ]

    source_cat = mc.setup_source_catalog()
    cat = mc.add_url_path(
        source_cat[config.model_name],
        timing=config.timing,
        start_date=config.start_date,
        end_date=config.start_date,
        # 404 like errors if you add end_date here?
        #        end_date=config.end_date
    )
    ds_model = cat[config.model_name].to_dask()
    ds_small = (
        ds_model
        .em.filter(config.standard_names)
        .em.sub_grid(bbox=bbox)
        .cf.sel(T=slice(config.start_date, config.end_date))
    )
    fname = (f'{config.model_name}_{config.timing}_'
             f'{config.start_date.strftime("%Y%m%d")}-'
             f'{config.end_date.strftime("%Y%m%d")}.nc')
    pth = output_dir / fname
    ds_small.to_netcdf(output_dir / fname)
    return pth


def run_fetch_data(start_date: pd.Timestamp,
                   end_date: pd.Timestamp,
                   output_dir: Path):
    """Parse the model config, then run fetch_data."""
    model_config = ModelConfig(start_date=start_date, end_date=end_date)
    output_pth = fetch_data(model_config, output_dir)
    print(output_pth)


def main():
    """Fetch LOOFS data and write output to `output_dir`."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('start_date', type=pd.Timestamp)
    parser.add_argument('end_date', type=pd.Timestamp)
    parser.add_argument('output_dir', type=Path)
    args = parser.parse_args()
    run_fetch_data(args.start_date, args.end_date, args.output_dir)
    return 0


if __name__ == '__main__':
    sys.exit(main())
