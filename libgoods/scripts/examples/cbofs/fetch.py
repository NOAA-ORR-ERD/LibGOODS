#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""Download model data with catalog."""
import sys
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

DEFAULT_BBOX = (-76.5, 36.75, -75.25, 37.75)
MODEL_NAME = 'CBOFS'


def main():
    """Fetch CBOFS Model Data."""
    # Check output
    output_dir = Path(__file__).parent / 'output'
    if not output_dir.exists():
        output_dir.mkdir()

    config = parse_config(main=main,
                          model_name=MODEL_NAME,
                          default_bbox=DEFAULT_BBOX,
                          output_dir=output_dir,
                          default_timing='hindcast',
                          standard_names=STANDARD_NAMES)
    fetch(config)
    return 0


if __name__ == '__main__':
    sys.exit(main())
