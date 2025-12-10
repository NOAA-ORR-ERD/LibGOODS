# NOTE: This program implements a method for the GNOME model to read and process the GLOFS output ncfile based on linear interpolation.
# The new method first does a triangulation based on the centroids of the triangular grids that are derived from the ncfile,
# and then use a projected-vector method to assign vectors at the boundary nodes.
# For better understanding of the method, the author classified four main calculation steps.
# Author: Yang Song;
# Email: soyang@umich.edu;
# Date of completion: 06/12/2024

import numpy as np
import netCDF4 as nc
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.tri as tri
from datetime import datetime
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import detect_points as dp
from matplotlib.path import Path
import gridded
from gridded.grids import UGrid
# from gridded.plotting.mpl_plotting import plot_ugrid
from matplotlib.tri import Triangulation
from matplotlib.collections import  LineCollection
import triangle
import math
import matplotlib
matplotlib.use('TKAgg') # Or 'Qt5Agg', 'Agg'，choose according to your requirements


# find border edges represented by the pairs of nodes
def find_border_edges(triangle_nodes):
    edges = set()
    for triangle in triangle_nodes:
        for i in range(3):
            edge = tuple(sorted([int(triangle[i]), int(triangle[(i + 1) % 3])]))
            if edge in edges:
                edges.remove(edge)
            else:
                edges.add(edge)
    return edges

# update/find the boundary node number after the new triangulation that uses centroids
def updated_boundaries(boundaries, new_nodes,lon,lat):
    new_boundaries = []  # Initialize new_boundaries as an empty list
    for boundary in boundaries:
        new_boundary = ([], [])
        node1, node2 = boundary
        for i, new_node in enumerate(new_nodes):
                if new_node[0] == lon[node1] and new_node[1] == lat[node1]:
                    new_boundary[0].append(i)
        for i, new_node in enumerate(new_nodes):
                if new_node[0] == lon[node2] and new_node[1] == lat[node2]:
                    new_boundary[1].append(i)

        new_boundaries.append(new_boundary)
        result = [(item1[0], item2[0]) for item1, item2 in new_boundaries]
    return result

# focus on the index problem
def find_index(triangle_nodes, edges):
    triangle_rows = []
    three_nodes_list = []
    sys_node_list=[]
    sys_centroid_list=[]
    for i, triangle in enumerate(triangle_nodes):
        three_nodes = []
        node=[]
        sys_node=[]
        for edge in edges:
            triangle_list = triangle.tolist()
            if edge[0] in triangle_list and edge[1] in triangle_list: # find the number of the triangle that contains boder_edges
                triangle_rows.append((i))
                node = [x for x in triangle_list if x != edge[0] and x != edge[1]]
                three_nodes=[int(edge[0]),int(edge[1]),node[0]] # find the vertice number of the triangle that contains boder_edges

                sys_node=find_symmetric_point(edge[0],edge[1],node[0], use_coordinates=False)
                sys_node_list.append(sys_node)
                three_nodes_list.append(three_nodes)

                centroid=[lonc[i],latc[i]]
                sys_centroid=find_symmetric_point(edge[0],edge[1],centroid, use_coordinates=True)
                sys_centroid_list.append(sys_centroid)
    return triangle_rows, three_nodes_list, sys_node_list, sys_centroid_list

# extract the nodes of the border_edges
def extract_border_nodes(border_edges):
    border_nodes = set()
    for edge in border_edges:
        border_nodes.update(edge)
    return list(border_nodes)


# compute the field value for the border node
def calculate_field_border(Field, nvt, border_node):
    Field_border = np.zeros(len(border_node))
    count = np.zeros(len(border_node))
    for i, node in enumerate(border_node):
        indices = np.where(nvt == node)[0]
        for index in indices:
            Field_border[i] += Field[index]
            count[i] += 1
    # 计算平均值
    for i in range(len(border_node)):
        if count[i] > 0:
            Field_border[i] /= count[i]
    return Field_border

# find the symmetric point of C relative to AB
def find_symmetric_point(A, B, C, use_coordinates=True):

    if use_coordinates:
        x3, y3 = C[0], C[1]
    else:
        x3, y3 = lon[C], lat[C]

    x1, y1 = lon[A],lat[A]
    x2, y2 = lon[B],lat[B]

    # if AB is vertical
    if x2 == x1:
        return (2 * x1 - x3, y3)
    # if AB is parallel
    elif y2 == y1:
        return (x3, 2 * y1 - y3)

    # compute the slope and the vertical bias of AB
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1

    m_perp = -1 / m
    b_perp = y3 - m_perp * x3

    xm = (b_perp - b) / (m - m_perp)
    ym = m * xm + b

    xd = 2 * xm - x3
    yd = 2 * ym - y3

    return (xd, yd)


# convert lonlat to cartesian coordinates
def lonlat_to_xy(lon, lat, R=6371):

    if not (-180 <= lon <= 180):
        raise ValueError("lon wrong")
    if not (-90 <= lat <= 90):
        raise ValueError("lat wrong")

    lat_radians = math.radians(lat)
    lon_radians = math.radians(lon)
    x = R * math.cos(lat_radians) * math.cos(lon_radians)
    y = R * math.cos(lat_radians) * math.sin(lon_radians)
    return x, y


# compute the projected vector that contains two components based on lonlat coordinates
def velocity_projection_2d(lon1, lat1, lon2, lat2, u, v, R=6371):

    # determine whether the coordinate conversion is needed
    x1, y1 = lonlat_to_xy(lon1,lat1, R)
    x2, y2 = lonlat_to_xy(lon2,lat2, R)
    # x1, y1 = lon1, lat1
    # x2, y2 = lon2, lat2

    B = np.array([x2 - x1, y2 - y1])
    length_B = np.linalg.norm(B)
    B_unit = B / length_B

    v_vector = np.array([u, v])

    projection_length = np.dot(v_vector, B_unit)
    projection_vector = projection_length * B_unit

    return projection_vector[0], projection_vector[1]
   # return projection_vector


def generate_new_velocity(u, v, three_nodes_list, border_nodes):
    u_border_list = []
    v_border_list = []
    node_indices = {node: [] for node in border_nodes}
    for i, node in enumerate(border_nodes):
        for j, three_nodes in enumerate(three_nodes_list):
            if node in three_nodes:
                node_indices[node].append(j)

    avg_u_border_list = []
    avg_v_border_list = []
    for node, indices in node_indices.items():

        total_u_border = 0
        total_v_border = 0
        count = 0

        for indice in indices:
            three_nodes = three_nodes_list[indice]
            node1 = three_nodes[0]
            node2 = three_nodes[1]

            # compute the vector at the boundary node using the vector at the boundary triangle center
            # and the projected method
            u_border, v_border = velocity_projection_2d(lon[node1], lat[node1], lon[node2], lat[node2],
                                                        u[triangle_rows[indice]], v[triangle_rows[indice]], R=6371)

            total_u_border += u_border
            total_v_border += v_border
            count += 1

        avg_u_border = total_u_border / count
        avg_v_border = total_v_border / count
        avg_u_border_list.append(avg_u_border)
        avg_v_border_list.append(avg_v_border)

    u_new = np.concatenate([u, avg_u_border_list])  # centroids plus boundary nodes
    v_new = np.concatenate([v, avg_v_border_list])

    return u_new, v_new


# the plot_ugrid function from Chris
def plot_ugrid(axes,
               grid,
               node_numbers=False,
               face_numbers=False):
    """
    plot a UGRID in the provided MPL axes

    :param axes: an MPL axes object to plot on

    :param grid: a gridded.Ugrid grid object to plot

    :param node_numbers=False: If True, plot the node numbers

    :param face_numbers=False: If True, plot the face numbers

    """

    nodes = grid.nodes
    # plot triangles (faces)
    mpl_tri = Triangulation(nodes[:, 0], nodes[:, 1], grid.faces)
    axes.triplot(mpl_tri)
    if face_numbers:
        if grid.face_coordinates is None:
            grid.build_face_coordinates()
        face_coords = grid.face_coordinates
        for i, point in enumerate(face_coords):
            axes.annotate(f"{i}", point,
                          xytext=(0, 0),
                          textcoords='offset points',
                          horizontalalignment='center',
                          verticalalignment='center',
                          bbox = {'facecolor': 'white', 'alpha': 1.0, 'boxstyle': "round,pad=0.0", 'ec': 'white'},
                          )

    # plot nodes
    axes.plot(nodes[:, 0], nodes[:, 1], 'o')
    if node_numbers:
        for i, point in enumerate(nodes):
            axes.annotate(f"{i}", point,
                          xytext=(2, 2),
                          textcoords='offset points',
                          bbox = {'facecolor': 'white', 'alpha': 1.0, 'boxstyle': "round,pad=0.0", 'ec': 'white'},
                          )

    # plot boundaries
    if grid.boundaries is not None:
        bounds = grid.boundaries
        lines = []
        for bound in bounds:
            lines.append([nodes[bound[0]], nodes[bound[1]]])
        lc = LineCollection(lines, linewidths=3, colors=(1, 0, 0, 1))
        # lc = LineCollection(lines), colors=c, linewidths=2)
        axes.add_collection(lc)



# Load basic information, can directly read in any GLOFS 3D output file
############################################
fn='./../erie_2019Sep15-17_3D.nc' # you can directly use any output ncfile from GLOFS for Lake Erie
ncfile = nc.Dataset(fn, 'r')
nodes_num=ncfile.dimensions['node'].__len__()
nv=ncfile.variables['nv'][:]-1
lat=ncfile.variables['lat'][:] # latitude at nodes
lon=ncfile.variables['lon'][:] # longitude at nodes
latc=ncfile.variables['latc'][:] # latitude at elements
lonc=ncfile.variables['lonc'][:] # longitude at elements
x=ncfile.variables['x'][:] 
y=ncfile.variables['y'][:] 
xc=ncfile.variables['xc'][:]
yc=ncfile.variables['yc'][:]
nvt=nv.transpose()
u = ncfile.variables['u'][0, 0, :]
v = ncfile.variables['v'][0, 0, :]
lon=lon-360.
lonc=lonc-360.

# set the region to focus
lonl=-82.85
latb=41.4
dlon=0.25
dlat=0.4
map_proj = ccrs.PlateCarree()
############################################




# Step 1: find boundary nodes and solve the index problem once and for all
############################################
border_edges = find_border_edges(nvt)
triangle_rows, three_nodes_list, sys_node_list, sys_centroid_list = find_index(nvt, border_edges)
border_nodes = extract_border_nodes(border_edges)
border_lon = lon[border_nodes]
border_lat = lat[border_nodes]
lonc1 = np.concatenate([lonc, border_lon])
latc1 = np.concatenate([latc, border_lat])
###############################################



# Step 2: use the projected method to assign vectors at the boundary nodes
############################################
u_new, v_new = generate_new_velocity(u, v, three_nodes_list, border_nodes)
############################################



# Step 3: create a new triangulation based on the centroids plus original border nodes
############################################
nodes=list(zip(lon, lat))
boundaries=list(border_edges)
holes = [[-82.663389, 41.76265],[-82.821783, 41.717806],[-82.812769, 41.68135],[-82.826072, 41.646322],[-82.703672, 41.601081]]
new_nodes=list(zip(lonc1, latc1))
new_boundaries= updated_boundaries(boundaries,new_nodes,lon,lat) # update index

triang0= triangle.triangulate({'vertices': new_nodes,
                             'segments': new_boundaries,
                             'holes': holes,
                             # 'regions': boundaries,
                             }, opts='p')

triangle_dict = triang0['triangles']
node_dict = triang0['vertices']
lon_dict = node_dict[:,0]
lat_dict = node_dict[:,1]

new_nodes=list(node_dict)
# Create a UGRID with the nodes and faces (triangles)
grid = UGrid(nodes=triang0['vertices'], faces=triang0['triangles'])

# find the boundaries (could have specified from above)
grid.build_boundaries()
############################################



# Step 4 (final calculation step): get the vectors at the nodes of the new triangulation, use the gridded function to
# linearly interpolate the values at designated vertical points
############################################
node_u = gridded.Variable(name='sample data on nodes',
                            units=None,
                            data=u_new,
                            grid=grid,
                            location='node',
                            )

node_v = gridded.Variable(name='sample data on nodes',
                            units=None,
                            data=v_new,
                            grid=grid,
                            location='node',
                            )

xloc=np.linspace(lonl+0.002,lonl+dlon,15)
yloc=np.linspace(latb+0.002,latb+dlat,200)
xloc,yloc=np.meshgrid(xloc,yloc)


xloc_ref=[]
yloc_ref=[]
nloc_ref=[]
valloc_u=[]
valloc_v=[]
valcent=[]

for jj in range(len(yloc[:,0])):
    for ii in range(len(xloc[0,:])):

        nel = grid.locate_faces((xloc[jj,ii],yloc[jj,ii]))

        if nel == -1:
                    valloc_u.append(np.nan)
                    valloc_v.append(np.nan)

                    valcent.append(np.nan)
                    xloc_ref.append(np.nan)
                    yloc_ref.append(np.nan)
                    nloc_ref.append(np.nan)

        else:

            # use the gridded interpolater
            points = np.c_[xloc[jj, ii], yloc[jj, ii]]
            FPTu = node_u.at(points)[:, 0]
            FPTv = node_v.at(points)[:, 0]
            FPTu = FPTu[0]
            FPTv = FPTv[0]

            valloc_u.append(FPTu)
            valloc_v.append(FPTv)

xloc=xloc.flatten()
yloc=yloc.flatten()
xloc=xloc[~np.isnan(valloc_v)]
yloc=yloc[~np.isnan(valloc_v)]
valloc_u=list(filter(lambda x: not np.isnan(x), valloc_u))
valloc_v=list(filter(lambda x: not np.isnan(x), valloc_v))
############################################







# NOTE: The codes below are only used for ploting and analyzing.
# Plot 1: the original triangulation, ghost cells, and centroid points
############################################
plt.figure(1, figsize=(18,10))
triang = tri.Triangulation(lon, lat, nvt)
plt.scatter(lon[border_nodes], lat[border_nodes], color='red', label='Boundary Nodes')
x_coords = [point[0] for point in sys_centroid_list]
y_coords = [point[1] for point in sys_centroid_list]
plt.scatter(x_coords, y_coords, color='black')
plt.triplot(triang,color='k')
for i, three_nodes in enumerate(three_nodes_list):
    node1 = three_nodes[0]
    node2 = three_nodes[1]
    x1, y1 = lon[node1],lat[node1]
    x2, y2 = lon[node2],lat[node2]
    x3, y3 = sys_node_list[i]
    plt.plot([x1, x2, x3, x1], [y1, y2, y3, y1], 'b-')
############################################




# Plot 2: the new triangulation
############################################
fig, axes = plt.subplots(1,)
fig.set_size_inches((20, 20))

plot_ugrid(axes, grid, node_numbers=False, face_numbers=False)

axes.set_xlim(-83, -82.5)
axes.set_ylim(41.5, 42)
############################################




# Plot 3: the interpolated u/v at the designated vertical points and compare them with constants within original triangles
###########################################
plt.figure(3, figsize=(18,10))
uminv=-0.2
umaxv=0.2
vminv=-0.2
vmaxv=0.2
ax = plt.subplot(121, projection=ccrs.PlateCarree())
extents = [lonl, lonl+dlon, latb, latb+dlat]
ax.set_extent(extents,crs=map_proj)
pp=ax.tripcolor(triang,u,cmap=plt.cm.get_cmap("jet"),vmin=uminv,vmax=umaxv)
ax.triplot(triang,color='k')
ax.scatter(lonc1,latc1,s=15,c=u_new,vmin=uminv,vmax=umaxv,edgecolor='k',cmap=plt.cm.get_cmap("jet"))
ax.scatter(xloc,yloc,s=18,c=valloc_u,vmin=uminv,vmax=umaxv,edgecolor='gray',cmap=plt.cm.get_cmap("jet"))
plt.colorbar(pp,shrink=0.3)
ax.set_title("interpolated U, constant within each triangle")
xticks = np.linspace(min(xloc), max(xloc), num=15)
yticks = np.linspace(min(yloc), max(yloc), num=50)
ax.set_xticks(xticks)
yticks_interval = yticks[::3]
ax.set_yticks(yticks_interval)
ax.set_xticklabels([f'{tick:.3f}' for tick in xticks], rotation=45)
ax.set_yticklabels([f'{tick:.3f}' for tick in yticks_interval])

ax2 = plt.subplot(122, projection=ccrs.PlateCarree())
extents = [lonl, lonl+dlon, latb, latb+dlat]
ax2.set_extent(extents,crs=map_proj)
p2=ax2.tripcolor(triang,v,cmap=plt.cm.get_cmap("jet"),vmin=vminv,vmax=vmaxv)
ax2.triplot(triang,color='k')
ax2.scatter(lonc1,latc1,s=15,c=v_new,vmin=vminv,vmax=vmaxv,edgecolor='k',cmap=plt.cm.get_cmap("jet"))
ax2.scatter(xloc,yloc,s=18,c=valloc_v,vmin=vminv,vmax=vmaxv,edgecolor='gray',cmap=plt.cm.get_cmap("jet"))
plt.colorbar(p2,shrink=0.3)
ax2.set_title("interpolated V, constant within each triangle")
ax2.set_xticks(xticks)
ax2.set_xticklabels([f'{tick:.3f}' for tick in xticks], rotation=45)
tit="interp_fvcominterpolator.png"
plt.tight_layout()
plt.savefig(tit,dpi=200)
fixed_x_value = xloc[1994]
indices = [i for i, x in enumerate(xloc) if x == fixed_x_value]
selected_yloc = [yloc[i] for i in indices]
selected_valloc_u = [valloc_u[i] for i in indices]
selected_valloc_v = [valloc_v[i] for i in indices]
###########################################




# Plot 4: u and v profiles
###########################################
plt.figure(4)
plt.scatter(selected_valloc_u, selected_yloc, color='r', label='u')
plt.scatter(selected_valloc_v, selected_yloc, color='b', label='v')
plt.title(f'xloc={fixed_x_value}')
plt.xlim(-1, 1)  # limit the x-axis range to (2, 4)
plt.ylabel('yloc')
plt.xlabel('Value')
plt.legend()
###########################################




# Plot 5: vector proflie
###########################################
plt.figure(5, figsize=(8,8))
ax = plt.subplot(111, projection=ccrs.PlateCarree())
extents = [lonl, lonl+dlon, latb, latb+dlat]
ax.set_extent(extents,crs=map_proj)
ax.triplot(triang, '-k')
fixed_x_value_list = np.full(len(selected_yloc), fixed_x_value)
a_fixed_x_value_list = fixed_x_value_list[::1]
a_selected_yloc= selected_yloc[::1]
a_selected_valloc_u = selected_valloc_u[::1]
a_selected_valloc_v = selected_valloc_v[::1]
ax.quiver(a_fixed_x_value_list , a_selected_yloc, a_selected_valloc_u, a_selected_valloc_v,
           units = 'xy', angles = 'xy', scale = 2, scale_units = 'xy', color = 'b', linewidths=0.0001)
xticks = np.linspace(min(xloc), max(xloc), num=15)
yticks = np.linspace(min(yloc), max(yloc), num=50)
ax.set_xticks(xticks)
yticks_interval = yticks[::3]
ax.set_yticks(yticks_interval)
ax.set_xticklabels([f'{tick:.3f}' for tick in xticks], rotation=45)
ax.set_yticklabels([f'{tick:.3f}' for tick in yticks_interval])
ax.axes.set_ylim(41.49, 41.63)
plt.show()
###########################################


