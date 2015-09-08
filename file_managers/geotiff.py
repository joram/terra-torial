import io
import os
from geopy.geocoders import Nominatim
import tifffile
import math
from file_managers.heightmap import Heightmap
from flask import make_response

# ASTER GDEM is a product of METI and NASA.


class GeoTiff(object):

    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.geolocator = Nominatim()
        self._pixels = None
        self.width = None
        self.height = None

        # parse lat/lng from filename
        position = self.filename
        for (a, b) in [
            ("ASTGTM2_", ""),
            (".tif", ""),
            ("_num", ""),
            ("_dem", ""),
            ("N", ""),
            ("S", "-"),
            ("E", ","),
            ("W", ",-")]:
            position = position.replace(a, b)
        self._lat, self._lng = position.split(",")
        self._lat = int(self._lat)
        self._lng = int(self._lng)
        self.sizes = [1.0/math.pow(2, s) for s in range(0, 30)]

    @property
    def pixels(self):
        
        # parse width, height, pixels from image
        if self._pixels == None:
            im = tifffile.TiffFile(self.filepath)
            self._pixels = im.asarray()
            self.width = len(self._pixels)
            self.height = len(self._pixels[0])
        return self._pixels

    @property
    def min_lat(self):
        return self._lat

    @property
    def max_lat(self):
        return self._lat + 1

    @property
    def min_lng(self):
        return self._lng

    @property
    def max_lng(self):
        return self._lng + 1

    @property
    def area(self):
        return self.min_lat, self.max_lat, self.min_lng, self.max_lng

    def contains(self, lat, lng):
        _ = self.pixels
        if not (self.min_lat <= lat <= self.max_lat):
            return False
        if not (self.min_lng <= lng <= self.max_lng):
            return False
        return True

    # def coords_to_xy(self, lat, lng, zoom):
    #     if not self.contains(lat, lng):
    #         return None
    #
    #     lat_ratio = abs(lat - self.min_lat)
    #     x = int(self.width*lat_ratio)
    #
    #     size = self.height*self.sizes[zoom]
    #     lng_ratio = abs(lng - self.min_lng)
    #     y = int(self.height * lng_ratio if lng_ratio > 0 else 0)
    #     print("%s\t ->\t%s" % ((lat, lng), (x, y)))
    #     return x, y
    
        # test = {}
        # test[(49.5, -123.5)] = (1800, 1800)
        # test[(49.0, -124.0)] = (0, 0)
        #
        # test[(48.5, -124.0)] = (1800, 1800)
        # test[(49.0, -123.5)] = (3601, 0)
        #
        # test[(49.0, -123.5)] = (0, 3601)
        # test[(49.5, -123.0)] = (1800, 1800)
        #
        # test[(48.0, -124.0)] = (0, 1800)
        # test[(48.5, -123.5)] = (1800, 0)
        #
        # return test.get((lat, lng))

    def subsection(self, y, x, zoom):
        _ = self.pixels

        num_tiles = int(1/self.sizes[zoom])
        ratio = self.sizes[zoom]
        tile_width = self.width*ratio

        x %= num_tiles
        y %= num_tiles
        y = (num_tiles - 1) - y

        min_x = tile_width*x
        min_y = tile_width*y
        max_x = min_x + tile_width
        max_y = min_y + tile_width
        return self.pixels[min_x:max_x, min_y:max_y]