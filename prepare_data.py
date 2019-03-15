import shapefile
import numpy as np
import math
import csv
import os
import shutil

patch_size = 128
offset_tolerance = 20

rows = 38300
cols = 40248

left = 1561776.7
right = 1573851.1
up = 5186889.225
down = 5175399.225

vertex_num_max = 25

# TODO: find out the exact ratio
# res_x = (right - left) / cols
res_y = (up - down) / rows
res_x = res_y


def filter_buildings(input_shapefile_path="/Users/czy/Dataset/WHU Building Dataset/data/shapefile/train_area/train.shp"):
    """

    :param input_shapefile_path: path to original shapefile
    :return: filtered shapefile
    """

    shp = shapefile.Reader(input_shapefile_path)
    Shapes = shp.shapes()
    polygon_num = len(Shapes)

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

        # TODO: check this
        index_x0 = math.floor((np.average(p, axis=0)[0] - left) / res_x / patch_size)
        index_y0 = math.floor((np.average(p, axis=0)[1] - down) / res_x / patch_size)

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

    w.save("/Users/czy/Desktop/filtered.shp")


def extract_one_building():
    pass


def create_annotations(input_shapefile_path="/Users/czy/Desktop/filtered.shp"):
    """

    :param input_shapefile_path: path to filtered shapefile
    :return:
    """

    shp = shapefile.Reader(input_shapefile_path)
    Shapes = shp.shapes()
    polygon_num = len(Shapes)

    # loop over all polygons
    for i in range(polygon_num):
        s = Shapes[i]
        p = s.points
        n_points = len(p) - 1

        # polygon center
        center = np.average(p, axis=0)
        n_tile = math.floor((center[0] - left) / res_x / patch_size) \
                 + math.floor((center[1] - down) / res_y / patch_size) * math.ceil(cols / patch_size)

        # the 1st number in each row represents the vertex quantity
        # supplement zeros afterwords
        coordinates = []
        zeros = [0 for i in range(2 * vertex_num_max - 2 * n_points)]

        # loop over all vertexes in one polygon
        for j in range(n_points):

            # original geo coordinates
            x = p[j][0]
            y = p[j][1]

            # coordinates relative to the whole area
            [pixel_x, pixel_y] = [round((x - left) / res_x), round((up - y) / res_y)]

            # patch index (start from 0)
            index_x = math.floor(pixel_x / patch_size)
            index_y = math.floor(pixel_y / patch_size)

            local_x = pixel_x - index_x * patch_size
            local_y = pixel_y - index_y * patch_size

            coordinates.append(local_y)
            coordinates.append(local_x)

        # write csv files
        file = open("/Users/czy/Desktop/polygons.csv", 'a', newline='')
        csvwriter = csv.writer(file)
        csvwriter.writerow([n_tile] + [n_points] + coordinates + zeros)
        # csvwriter.writerow([n_points] + [n_tile])
        file.close()


def copy_files(index_path='/Users/czy/Dataset/DSAC/polygons/scheme2/polygons_index.csv', file_type="image"):

    if file_type == "mask":
        src_dir = "/Users/czy/Dataset/DSAC/_masks/masks/"
        dst_dir = "/Users/czy/Dataset/DSAC/masks/"
    elif file_type == "image":
        src_dir = "/Users/czy/Dataset/DSAC/_images/images/"
        dst_dir = "/Users/czy/Dataset/DSAC/images/"

    with open(index_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        indexes = [row[0] for row in reader]
        filenames = ["building_" + str(indexes[i]) + ".TIF" for i in range(len(indexes))]
        for filename in filenames:
            shutil.copyfile(src_dir + filename, dst_dir + filename)


if __name__ == '__main__':
    # create_annotations()
    # filter_buildings()
    copy_files()
