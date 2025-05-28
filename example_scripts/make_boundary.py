"""
This is a one-off script that I used to generate the boundary for SSCOFS. Some of it could be leveraged into a utility that takes
the boundary lat/lons for each model and writes the info the metadata yaml file.
"""
from libgoods.file_processing import tri_model
import numpy as np
import shapely
from shapely.geometry import shape, mapping

path2file = 'C:\\Users\\amy.macfadyen\PyProjects\libgoods\example_scripts\OFS_results\SSCOFS\sscofs.t03z.20250501.fields.f001.nc'
sscofs = tri_model.tri()
sscofs.open_nc(path2file)
sscofs.get_dimensions()
sscofs.get_grid_topo()
bnd = sscofs.find_bndry_segs()
sscofs.order_boundary(bnd)
blon,blat = sscofs.get_bnd_coords()

#Thin boundary as required (10 km spacing is default)
bnd_res = 10
tblon = [blon[0],]; tblat = [blat[0],];

for ii in range(1,len(blon)):
        dx = (blon[ii] - tblon[-1]) * 111.325 * np.cos(blat[ii]*np.pi/180)
        dy = (blat[ii] - tblat[-1]) * 111.325
        d = np.sqrt(dx**2 + dy**2)
        if d > bnd_res:
            tblon.append(blon[ii])
            tblat.append(blat[ii])

ll = np.column_stack((tblon,tblat))
poly = shapely.Polygon(ll)

# convert to GeoJSON format
geojson = mapping(poly)
geojson['coordinates'] = np.round(np.array(geojson['coordinates']),4)

with open('sscofs_bry_wktr.txt','w') as f:
      f.write(shape(geojson).wkt)
