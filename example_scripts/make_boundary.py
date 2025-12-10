"""
This is an example that can be used to generate the boundary for ROMS or FVCOM models.
Its using utilties in the older nc4 "file_processing" classes
"""
from libgoods.file_processing import tri_model, roms_model
from libgoods.utilities import thin_and_write_bnd

#ROMS
url = 'https://gcoos5.geos.tamu.edu/thredds/dodsC/ROFS_latest/txla2_his_f_latest.nc'
tamu = roms_model.roms()
tamu.open_nc(url)
tamu.get_dimensions()
blon, blat = tamu.get_bdry()


#FVCOM (this one is slow)
path2file = 'C:\\Users\\amy.macfadyen\PyProjects\libgoods\example_scripts\OFS_results\SSCOFS\sscofs.t03z.20250501.fields.f001.nc'
sscofs = tri_model.tri()
sscofs.open_nc(path2file)
sscofs.get_dimensions()
sscofs.get_grid_topo()
bnd = sscofs.find_bndry_segs()
sscofs.order_boundary(bnd)
blon,blat = sscofs.get_bnd_coords()

thin_and_write_bnd(blon, blat)