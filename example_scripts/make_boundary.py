from libgoods.file_processing import tri_model
import numpy as np


path2file = 'C:\\Users\\amy.macfadyen\PyProjects\libgoods\example_scripts\OFS_results\SSCOFS\sscofs.t03z.20250501.fields.f001.nc'
sscofs = tri_model.tri()
sscofs.open_nc(path2file)
sscofs.get_dimensions()
sscofs.get_grid_topo()
bnd = sscofs.find_bndry_segs()
sscofs.order_boundary(bnd)
lon,lat = sscofs.make_bnd_poly()

#Thin boundary as required (10 km spacing is default)
bnd_res = 10
sf = 4
tblon = [blon[0],]; tblat = [blat[0],];

for ii in range(1,len(blon)):
        dx = (blon[ii] - tblon[-1]) * 111.325 * np.cos(blat[ii]*np.pi/180)
        dy = (blat[ii] - tblat[-1]) * 111.325
        d = np.sqrt(dx**2 + dy**2)
        if d > bnd_res:
            tblon.append(blon[ii].round(sf))
            tblat.append(blat[ii].round(sf))