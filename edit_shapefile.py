import shapefile
import numpy as np
import math

shp = shapefile.Reader("/Users/czy/Dataset/WHU Building Dataset/data/shapefile/train_area/train.shp")
Shapes = shp.shapes()
polygon_num = len(Shapes)
patch_size = 128
offset_tolerance = 20

rows = 38300
cols = 40248

left = 1561776.7
right = 1573851.1
up = 5186889.225
down = 5175399.225

res_x = (right - left) / cols
res_y = (up - down) / rows

w = shapefile.Writer(shapefile.POLYGON)
w.autoBalance = 1
w.field('FIRST_FLD', 'C', '40')

for i in range(polygon_num):
    s = Shapes[i]
    p = s.points
    n_points = len(p) - 1
    joints = []

    # a flag to verify if all vertexes belong to the same patch
    IS_SAME_PATCH = True

    index_x0 = math.floor((p[0][0] - left) / res_x / patch_size)
    index_y0 = math.floor((p[0][1] - down) / res_x / patch_size)

    # loop over the vertexes to update the flag or not
    for v in range(len(p)):
        index_x = math.floor((p[v][0] - left) / res_x / patch_size)
        index_y = math.floor((p[v][1] - down) / res_x / patch_size)

        if index_x != index_x0 or index_y != index_y0:
            IS_SAME_PATCH = False
            break
        else:
            pass

    # polygon located at the patch center and all vertexes belong to the same patch
    if abs((np.average(p, axis=0)[0] - left) / res_x % patch_size - patch_size / 2) <= offset_tolerance \
            and abs((np.average(p, axis=0)[1] - down) / res_y % patch_size - patch_size / 2) <= offset_tolerance \
            and IS_SAME_PATCH:
        for j in range(n_points):
            joints.append([p[j][0], p[j][1]])
        w.poly(parts=[joints])
        w.record('')

w.save("/Users/czy/Desktop/new.shp")