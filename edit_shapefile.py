import shapefile
import numpy as np

shp = shapefile.Reader("/Users/czy/Dataset/WHU Building Dataset/data/shapefile/train_area/train.shp")
Shapes = shp.shapes()
polygon_num = len(Shapes)
patch_size = 128
offset_tolerance = 20

w = shapefile.Writer(shapefile.POLYGON)
w.autoBalance = 1
w.field('FIRST_FLD', 'C', '40')

for i in range(polygon_num):
    s = Shapes[i]
    p = s.points
    n_points = len(p) - 1
    joints = []
    if abs(np.average(p, axis=0)[0] % patch_size - patch_size / 2) <= offset_tolerance \
            and abs(np.average(p, axis=0)[1] % patch_size - patch_size / 2) <= offset_tolerance:
        for j in range(n_points):
            joints.append([p[j][0], p[j][1]])
        w.poly(parts=[joints])
        w.record('')

w.save("/Users/czy/Desktop/new.shp")