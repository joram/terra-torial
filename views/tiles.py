import os
import io
from osgeo import gdal

from file_managers.geotiff import GeoData

gdal.UseExceptions()
import Image
import numpy
import math


class GeoTiffManager(object):

    def __init__(self):
        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        self.geotiff_dir = os.path.join(self.base_dir, "data/astergdem2")
        self.powers_of_two = [math.pow(2, power) for power in range(0, 10)]
        self.geotiffs = {}
        for filename in os.listdir(self.geotiff_dir):
            if filename.endswith("_dem.tif"):
                filepath = os.path.join(self.geotiff_dir, filename)
                location = self._filepath_to_location(filepath)
                self.geotiffs[location] = filepath

    def _filepath_to_location(self, filepath):
        filename = os.path.basename(filepath)
        for (a, b) in [("ASTGTM2_", ""), ("_dem.tif", ""), ("N", ""), ("W", ", -")]:
            filename = filename.replace(a, b)
        lat, lng = filename.split(", ")
        lat = int(lat) % 360
        lng = (int(lng)-90) % 180
        return lat, lng

    def tile_segments(self, zoom):

        num_tiles_x = [x*360 for x in self.powers_of_two][zoom]
        num_tiles_y = [x*180 for x in self.powers_of_two][zoom]
        return num_tiles_x, num_tiles_y

    def normalize_tile_coordinates(self, x, y, zoom):
        num_tiles_x, num_tiles_y = self.tile_segments(zoom)
        x2 = x % num_tiles_x
        y2 = y % num_tiles_y
        return x2, y2

    def filepath(self, x, y, zoom):
        x, y = self.normalize_tile_coordinates(x, y, zoom)
        return os.path.join(self.base_dir, "static/images/tiles/zoom_%s/%s_%s.jpg" % (zoom, int(x), int(y)))

    def build_tile(self, x, y, zoom):

        print x, y
        num_tiles_x, num_tiles_y = self.tile_segments(zoom)
        x, y = self.normalize_tile_coordinates(x, y, zoom)
        print x, y

        lat = 360*x*self.powers_of_two[zoom]/num_tiles_x
        lng = 180*y/num_tiles_y

        tile_x = int(math.floor(lat))
        tile_y = int(math.floor(lng))
        segments_in_tile = [math.pow(2, power) for power in range(0, 10)][zoom]
        #
        # print("lat/lng is %s/%s" % (lat, lng))
        # print("at zoom %s, there is %s segments per tile" % (zoom, segments_in_tile))
        # print("at this zoom (%s), the map is %s tiles wide, and %s tiles tall" % (zoom, num_tiles_x, num_tiles_y))
        # print("%s, %s is in the (%s, %s) tile" % (x, y, tile_x, tile_y))

        print(tile_x, tile_y)
        if (tile_x, tile_y) in self.geotiffs.keys():
            print("we have the file")
            source_filepath = self.geotiffs[(tile_x, tile_y)]
            dest_filepath = self.filepath(x, y, zoom)
            self.save_slice(source_filepath, dest_filepath, x % segments_in_tile, y % segments_in_tile)

    def save_slice(self, source_filepath, dest_filepath, segment_x, segment_y):
        ds = gdal.Open(source_filepath)
        full_data = ds.ReadAsArray()


geotiffs = GeoData()
base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
sizes = [1.0/math.pow(2, x) for x in range(0, 30)]


def array_to_jpg(data):
    data = numpy.array(data)
    rescaled = (255.0 / data.max() * (data - data.min())).astype(numpy.uint8)
    img = Image.fromarray(rescaled)
    img = img.resize((256, 256), Image.ANTIALIAS)
    return img


def get_tile_data(x, y, zoom):
    size = sizes[zoom]
    lat = 48.0 + float(y)*size - size
    lng = -123.0 + float(x)*size - size
    lat += size
    lng += size

    if geotiffs.exists(lat, lng):
        min_coords = (lat, lng)
        max_coords = (lat+size, lng+size)
        data = geotiffs.heights(min_coords, max_coords)
        if data != None:
            img = array_to_jpg(data)
            output = io.BytesIO()
            img.save(output, format="JPEG")
            return output.getvalue()

