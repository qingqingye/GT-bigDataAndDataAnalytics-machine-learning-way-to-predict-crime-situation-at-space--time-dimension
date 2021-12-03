import math, os, sys, math
import numpy as np
from datetime import datetime
import settings as sett, kde as kde
from scipy import spatial

#initialize global variables
sett.init()
final_result = []
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#read parameters
pFile = open('files/parameterFile.txt', "r")
pFile.readline()
pList = pFile.readline().split("\t")

sett.p1 = float(pList[0])	# p1 = spatial bandwidth
sett.p2 = float(pList[1])	# p2 = temporal bandwidth
sett.p3 = float(pList[2])	# p3 = spatial resolution
sett.p4 = int(float(pList[3].strip()))	# p4 = temporal resolution

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#create output directory
sett.dir1 = 'outFiles'
if not os.path.exists(sett.dir1):
    os.makedirs(sett.dir1)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#read input point file
pFile = open('files/data.txt', "r")
inX, inY, inT = [], [], []
r = pFile.readline().split(",")
xmin, xmax, ymin, ymax, zmin, zmax = float(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5].strip())

for record in pFile:   
	inX.append(float(record.split(",")[0]))
	inY.append(float(record.split(",")[1]))
	inT.append([float(record.split(",")[2])])

pFile.close()
inXY = list(zip(inX, inY))

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#open output files   
stkdeFile = open('outFiles/stkde.txt', "w")
timeFile = open('outFiles/time.txt', 'w')

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#set global variables
sett.npts = len(inX)
sett.ct1 = 0.5 * math.pi
sett.ct2 = pow(10.0, 5) / (sett.npts * pow(sett.p1, 2) * sett.p2)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#STKDE

xminDiff = xmin%sett.p3
xmaxDiff = xmax%sett.p3
yminDiff = ymin%sett.p3
ymaxDiff = ymax%sett.p3
zminDiff = zmin%sett.p4
zmaxDiff = zmax%sett.p4

xminP = xmin - xminDiff + sett.p3
xmaxP = xmax - xmaxDiff + sett.p3
yminP = ymin - yminDiff + sett.p3
ymaxP = ymax - ymaxDiff + sett.p3
zminP = zmin - zminDiff + sett.p4
zmaxP = zmax - zmaxDiff + sett.p4

print (xmax)

t1 = datetime.now() 

#grids
xyGrid = []
for i in np.arange(int(xminP),int(xmaxP),sett.p3):
    for j in np.arange(int(yminP),int(ymaxP),sett.p3):
        xyGrid.append([i,j])
tGrid = []
for k in range(int(zminP),int(zmaxP),sett.p4):
    tGrid.append([k])

t2 = datetime.now()

#build trees
stree = spatial.cKDTree(inXY)
ttree = spatial.cKDTree(inT)

print(xyGrid[:9])

#nn queries
sList = stree.query_ball_point(xyGrid, sett.p1)
tList = ttree.query_ball_point(tGrid, sett.p2)

stList = []

t3 = datetime.now()

i = 0
while i < len(sList):	#loop though list of spatial neighbors (there is a list of neighbors for each xyGrid-point)
    j = 0
    while j < len(tList):	#loop through list of temporal neighbors (there is a list of neighbors for each tGrid-point)
        nList = [val for val in sList[i] if val in tList[j]]	#check for points that are neighbors spatially, as well as temporally
        xC, yC, zC = xyGrid[i][0], xyGrid[i][1], tGrid[j]		#fetch grid point
        density = 0.0
        if nList:
            for k in nList:
                nindex = int(k)
                density += kde.densityF(inXY[nindex][0], inXY[nindex][1], inT[nindex][0], xC, yC, zC[0])
            stkdeFile.write(str(xC) + "," + str(yC) + "," + str(zC[0]) + "," + str(density) +"\n")
            final_result.append([xC, yC, zC, density])
        j = j + 1
    i = i + 1

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm
# plt.rcParams["figure.figsize"] = [7.00, 3.50]
# plt.rcParams["figure.autolayout"] = True
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
x = [x[0] for x in final_result]
y = [x[1] for x in final_result]
z = [x[2][0] for x in final_result]
c = [x[3] for x in final_result]
# print(final_result)
# img = ax.scatter(x, y, z, c=c, cmap=cm.hot, alpha=0.3)
# plt.show()

import matplotlib
from scipy.interpolate import griddata
index_x = 0; index_y = 1; index_z = 2; index_c = 3;
list_name_variables = ['x', 'y', 'z', 'c'];
name_color_map = 'seismic';
# X-Y are transformed into 2D grids. It's like a form of interpolation
x1 = np.linspace(min(x), max(x), len(np.unique(x)));
y1 = np.linspace(min(y), max(y), len(np.unique(y)));
x2, y2 = np.meshgrid(x1, y1);

# Interpolation of Z: old X-Y to the new X-Y grid.
# Note: Sometimes values ​​can be < z.min and so it may be better to set
# the values too low to the true minimum value.
z2 = griddata( (x, y), z, (x2, y2), method='cubic', fill_value = 0);
z2[z2 < min(z)] = min(z);

# Interpolation of C: old X-Y on the new X-Y grid (as we did for Z)
# The only problem is the fact that the interpolation of C does not take
# into account Z and that, consequently, the representation is less
# valid compared to the previous solutions.
c2 = griddata( (x, y), c, (x2, y2), method='cubic', fill_value = 0);
c2[c2 < min(c)] = min(c);

#--------
color_dimension = c2; # It must be in 2D - as for "X, Y, Z".
minn, maxx = color_dimension.min(), color_dimension.max();
norm = matplotlib.colors.Normalize(minn, maxx);
m = plt.cm.ScalarMappable(norm=norm, cmap = name_color_map);
m.set_array([]);
fcolors = m.to_rgba(color_dimension);

# At this time, X-Y-Z-C are all 2D and we can use "plot_surface".
fig = plt.figure(); ax = fig.gca(projection='3d');
surf = ax.plot_surface(x2, y2, z2, facecolors = fcolors, linewidth=0, rstride=1, cstride=1,
                       antialiased=False);
cbar = fig.colorbar(m, shrink=0.5, aspect=5);
cbar.ax.get_yaxis().labelpad = 15; cbar.ax.set_ylabel(list_name_variables[index_c], rotation = 270);
ax.set_xlabel(list_name_variables[index_x]); ax.set_ylabel(list_name_variables[index_y]);
ax.set_zlabel(list_name_variables[index_z]);
plt.title('%s in fcn of %s, %s and %s' % (list_name_variables[index_c], list_name_variables[index_x], list_name_variables[index_y], list_name_variables[index_z]) );
plt.show();

t4 = datetime.now()
delta_t1_2 = t2 - t1
delta_t2_3 = t3 - t2
delta_t3_4 = t4 - t3

timeFile.write(str(delta_t1_2) + "," + str(delta_t2_3) + "," + str(delta_t3_4) + "\n")
timeFile.close()
stkdeFile.close()


    

        
        
