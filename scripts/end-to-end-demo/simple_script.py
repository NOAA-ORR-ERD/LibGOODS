"""
simple_script.py

About the simplest script you can write
"""
from datetime import datetime

import gnome.scripting as gs

FNAME = 'output/LOOFS_forecast_20220519-20220522.nc'
start_time = datetime(2022, 5, 19)

model = gs.Model(start_time=start_time,
                 duration=gs.days(3),
                 time_step=gs.minutes(15)
                 )

# the base GnomeMap is all water, no land
# you can optionally add boundaries
model.map = gs.GnomeMap(map_bounds=((-77, 38.5), (-77, 40),
                                    (-76, 40), (-76, 38.5))
                        )

# The very simplest mover: a steady uniform current
#velocity = (.2, 0, 0) #(u, v, w) in m/s
#uniform_vel_mover = gs.SimpleMover(velocity)
model_vel_mover = gs.PyCurrentMover.from_netCDF(FNAME)

#  random walk diffusion -- diffusion_coef in units of cm^2/s
random_mover = gs.RandomMover(diffusion_coef=2e4)

# add the movers to the model
model.movers += model_vel_mover
model.movers += random_mover

# create spill
spill = gs.surface_point_line_spill(release_time=start_time,
                                    start_position=(-76.5, 39.25, 0),
                                    num_elements=1000)
# add it to the model
model.spills += spill

# create an outputter: this renders png files and an animated gif
renderer = gs.Renderer(output_dir='./output/',
                       output_timestep=gs.hours(6),
                       # bounding box for the output images
                       map_BB=((-77, 38.5), (-77, 40),
                               (-76, 40), (-76, 38.5)))

model.outputters += renderer

# run the model
model.full_run()
