#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
simple_script.py

About the simplest script you can write
"""
import sys
from pathlib import Path
from argparse import ArgumentParser
from datetime import datetime

import cftime
import netCDF4 as nc4
import gnome.scripting as gs


def main():
    """Run a GNOME model using LOOFS forecast data."""
    parser = ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "forcing_file",
        type=Path,
        nargs="?",
        default=None,
        help="Forcing file for the model.",
    )
    args = parser.parse_args()
    if args.forcing_file is not None and not args.forcing_file.exists():
        raise FileNotFoundError(f"No such file: {args.forcing_file}")
    # This will raise if there's something structurally wrong with the input
    if args.forcing_file is not None:
        with nc4.Dataset(args.forcing_file, "r") as nc:
            calendar = getattr(nc["time"], "calendar", "standard")
            start_time = cftime.num2pydate(
                nc["time"][0], units=nc["time"].units, calendar=calendar
            )
    else:
        start_time = datetime(2022, 5, 13)

    model = gs.Model(
        start_time=start_time, duration=gs.days(3), time_step=gs.minutes(15)
    )

    # the base GnomeMap is all water, no land
    # you can optionally add boundaries
    bbox = ((-78.8, 43.5), (-78.8, 43.8), (-77.5, 43.8), (-77.5, 43.5))
    model.map = gs.GnomeMap(map_bounds=bbox)

    # The very simplest mover: a steady uniform current
    if args.forcing_file is not None:
        model_vel_mover = gs.PyCurrentMover.from_netCDF(
            args.forcing_file, surface_index=19
        )
        model.movers += model_vel_mover
    else:
        velocity = (0.2, 0, 0)  # (u, v, w) in m/s
        uniform_vel_mover = gs.SimpleMover(velocity)
        model.movers += uniform_vel_mover

    #  random walk diffusion -- diffusion_coef in units of cm^2/s
    random_mover = gs.RandomMover(diffusion_coef=2e4)

    # add the movers to the model
    model.movers += random_mover

    # create spill
    spill = gs.surface_point_line_spill(
        release_time=start_time, start_position=(-78.1, 43.65, 0), num_elements=1000
    )
    # add it to the model
    model.spills += spill

    # create an outputter: this renders png files and an animated gif
    renderer = gs.Renderer(
        output_dir="./output/",
        output_timestep=gs.hours(6),
        # bounding box for the output images
        map_BB=bbox,
    )

    model.outputters += renderer

    # run the model
    model.full_run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
