#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run a PyGnome scenario using CIOFS data.
"""
import sys
from pathlib import Path
from argparse import ArgumentParser

import cftime
import netCDF4 as nc4
import gnome.scripting as gs


def default_output() -> Path:
    """Return the default output path."""
    data_output_dir = Path(__file__).parent / 'output'
    filename = 'CIOFS_hindcast_20220620-20220621.nc'
    return data_output_dir / filename


def main():
    """Run basic PyGnome scenario using CIOFS data."""
    parser = ArgumentParser(description=main.__doc__)
    parser.add_argument('data_file',
                        type=Path,
                        default=default_output(),
                        nargs='?',
                        help='The CIOFS model output.')
    parser.add_argument('--diffusion-coefficient',
                        type=float,
                        default=2e4,
                        help='Specify diffusion coefficient')
    args = parser.parse_args()
    bbox = ((-154.5, 58.), (-154.5, 60.), (-151., 60.), (-151., 58.))
    spill_start_position = (-153., 59.)
    data_output_dir = Path(__file__).parent / 'output'

    print('Reading start time from model output')
    with nc4.Dataset(args.data_file, 'r') as nc:
        calendar = getattr(nc['ocean_time'], 'calendar', 'standard')
        start_time = cftime.num2pydate(nc['ocean_time'][0],
                                       units=nc['ocean_time'].units,
                                       calendar=calendar)

    print('Scenario Parameters')
    print(f'\tstart_time: {start_time:%Y-%m-%d %H:%M:%S}')
    print('\tduration: 16 hours')
    print('\tΔt: 15 min')
    print('\tBBOX:', bbox[0], bbox[3])
    print('\tSpill Location:', spill_start_position)
    model = gs.Model(start_time=start_time, duration=gs.hours(16), time_step=gs.minutes(15))
    model.map = gs.GnomeMap(map_bounds=bbox)
    print('Adding Current Mover from model data')
    model.movers += gs.PyCurrentMover.from_netCDF(args.data_file)
    model.movers += gs.RandomMover(diffusion_coef=args.diffusion_coefficient)

    print('Adding spill')
    spill = gs.surface_point_line_spill(release_time=start_time,
                                        start_position=spill_start_position,
                                        num_elements=1000)
    model.spills += spill
    print('Adding renderer')
    renderer = gs.Renderer(output_dir=str(data_output_dir),
                           output_timestep=gs.minutes(30),
                           map_BB=bbox)
    model.outputters += renderer
    print('Running scenario')
    model.full_run()
    print('Done')
    return 0


if __name__ == '__main__':
    sys.exit(main())
