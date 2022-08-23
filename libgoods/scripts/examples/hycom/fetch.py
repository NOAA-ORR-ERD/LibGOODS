#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""Download model data with catalog."""
import sys
from datetime import datetime, date, timedelta
from pathlib import Path

import extract_model  # noqa

from model_catalogs.examples import fetch, parse_config

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

DEFAULT_BBOX = (-79.10 + 360, 31.84, -68.159 + 360, 42.29)
MODEL_NAME = 'HYCOM'


def main():
    """Fetch HYCOM Model Data."""
    # Check output
    output_dir = Path(__file__).parent / 'output'
    if not output_dir.exists():
        output_dir.mkdir()

    default_start = date.today() - timedelta(days=2)
    default_end = date.today() - timedelta(days=1)

    config = parse_config(main=main,
                          model_name=MODEL_NAME,
                          default_bbox=DEFAULT_BBOX,
                          output_dir=output_dir,
                          default_timing='forecast',
                          standard_names=STANDARD_NAMES,
                          default_start=default_start,
                          default_end=default_end)
    fetch(config)
    return 0


if __name__ == '__main__':
    sys.exit(main())
