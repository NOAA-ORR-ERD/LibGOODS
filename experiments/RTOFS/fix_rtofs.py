
"""
cf_role grid_topology
topology_dimension  2
node_dimensions node_dimension1 node_dimension2
face_dimensions face_dimension1:node_dimension1 (padding:type1) face_dimension2:node_dimension2 (padding:type2)


node_coordinates

nodes: padding none

dimensions:
    time = UNLIMITED ;
    inode = 10 ;
    jnode = 20 ;
    icell = 9 ;
    jcell = 19 ;

variables:
    char time(time) ;
        time:standard_name = "time" ;
        time:long_name = "time" ;
        time:units = "seconds since 2015-01-01 00:00:00" ;
    float u(time, jcell, inode) ;
        u:description = "x-velocity" ;
        u:units = "m s-1" ;
        u:grid = "MyGrid" ;
        u:location = "edge1" ;
    float v(time, jnode, icell) ;
        u:description = "y-velocity" ;
        u:units = "m s-1" ;
        u:grid = "MyGrid" ;
        u:location = "edge2" ;
    float c(time, jcell, icell) ;
        c:description = "some concentration" ;
        c:grid = "MyGrid" ;
        c:location = "face" ;
    float node_lat(jnode, inode) ;
        node_lat:standard_name = "latitude" ;
        node_lat:units = "degree_north" ;
    float node_lon(jnode, inode) ;
        node_lon:standard_name = "longitude" ;
        node_lon:units = "degree_east" ;

    int MyGrid ;
        grid:cf_role = grid_topology
        grid:topology_dimension = 2 ;
        grid:node_dimensions = "inode jnode" ;
        grid:face_dimensions = "icell: inode (padding: none) jcell: jnode (padding: none)" ;
        grid:node_coordinates = "node_lon node_lat" ;

"""

import xarray as xr



ds = xr.open_dataset("sample_rtofs_offset_fixed.nc")

grid_topology = xr.DataArray(
    data = 1,
#    coords: 'Sequence[Sequence | pd.Index | DataArray | Variable | np.ndarray] | Mapping | None' = None,

#    dims: 'str | Iterable[Hashable] | None' = None,
    name = 'grid_topology',
    attrs = {"cf_role": "grid_topology",
            "topology_dimension": 2,
            "node_dimensions": "y x",
            "node_coordinates": "lon lat",
            }
            )

ds['grid_topology'] = grid_topology

# # remove scale-offset encoding:
# for var_name in ('water_u', 'water_v'):
#     old_var = ds[var_name]
#     print(old_var.encoding)
#     new_arr = xr.DataArray(data=old_var.data,
#                            coords =  old_var.coords,
#                            dims=old_var.dims,
#                            name=var_name,
#                            attrs=old_var.attrs,
#                            )
#     ds[var_name] = new_arr
#     print(ds[var_name].encoding)

ds.to_netcdf("rtofs_example_with_top.nc")




