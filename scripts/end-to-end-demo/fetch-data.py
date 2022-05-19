from dataclasses import dataclass, field
from pathlib import Path

import xarray as xr
import pandas as pd

import extract_model as em
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


def fetch_data(config: ModelConfig, output_dir: Path):
    """Fetch data for a given model configuration and save to output dir as netcdf file."""
    bbox = [config.lon_range[0], config.lat_range[0], config.lon_range[1], config.lat_range[1]]

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
    ds_small = (ds_model
        .em.filter(config.standard_names)
        .em.sub_grid(bbox=bbox)
        .cf.sel(T=slice(config.start_date, config.end_date))
    )

    fname = f'{config.model_name}_{config.timing}_{config.start_date.strftime("%Y%m%d")}-{config.end_date.strftime("%Y%m%d")}.nc'
    ds_small.to_netcdf(output_dir / fname)


def main(start_date: pd.Timestamp, end_date: pd.Timestamp, output_dir: Path):
    model_config = ModelConfig(start_date=start_date, end_date=end_date)
    fetch_data(model_config, output_dir)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('start_date', type=str)
    parser.add_argument('end_date', type=str)
    parser.add_argument('output_dir', type=Path)
    args = parser.parse_args()
    start_date = pd.Timestamp(args.start_date)
    end_date = pd.Timestamp(args.end_date)
    main(start_date, end_date, args.output_dir)
