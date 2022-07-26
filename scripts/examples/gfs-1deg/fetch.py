#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""Download model data with catalog."""
import sys
import pandas as pd
from pathlib import Path

import extract_model  # noqa

from model_catalogs.examples import fetch, parse_config

STANDARD_NAMES = [
    'wind_u',
    'wind_v',
    'longitude',
    'latitude',
]

DEFAULT_BBOX = (275., 25., 300., 48.)
MODEL_NAME = 'GFS-1DEG'


def main():
    """Fetch DBOFS Model Data."""
    # Check output
    output_dir = Path(__file__).parent / 'output'
    if not output_dir.exists():
        output_dir.mkdir()

    default_start = (pd.Timestamp.today() - pd.Timedelta('1D')).floor('1D') 
    default_end = default_start + pd.Timedelta('1D')

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
