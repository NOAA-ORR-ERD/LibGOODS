import gnome.scripting as gs

curr = gs.GridCurrent.from_netCDF('SSCOFS_subset.nc')

# In [11]: curr.grid.nodes.max(0)
# Out[11]: array([236.7129364 ,  49.51980591])

# In [12]: curr.grid.nodes.min(0)
# Out[12]: array([232.96643066,  46.72851181])

center = (curr.grid.nodes.min(0) + curr.grid.nodes.max(0)) / 2


mover = gs.CurrentMover(curr)

model = gs.Model(start_time=curr.data_start)
model.spills += gs.point_line_spill(num_elements=10,
                                    start_position=center,
                                    release_time=curr.data_start,
                                    )
model.full_run()




