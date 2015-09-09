import io
import os
from geopy.geocoders import Nominatim
import tifffile
import math
from file_managers.heightmap import Heightmap
from flask import make_response

# ASTER GDEM is a product of METI and NASA.

offset_lat = 48
offset_lng = -123

class GeoTiff(object):

    def __init__(self, filepath):
        self.sizes = [1.0/math.pow(2, s) for s in range(0, 30)]
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.geolocator = Nominatim()
        self._width = None
        self._height = None
        self._pixels = None
        self._coords = None

    def load_file_data(self):
        if self._pixels == None:
            im = tifffile.TiffFile(self.filepath)
            self._pixels = im.asarray()
            self._width = len(self._pixels)
            self._height = len(self._pixels[0])
    @property
    def pixels(self):
        if self._pixels == None:
            self.load_file_data()
        return self._pixels

    @property
    def width(self):
        if self._width == None:
            self.load_file_data()
        return self._width

    @property
    def height(self):
        if self._height == None:
            self.load_file_data()
        return self._height

    @property
    def coords(self):
        if self._coords == None:
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
            lat, lng = position.split(",")
            lat = int(lat)
            lng = int(lng)
            y = -(lat - offset_lat)
            x = (lng - offset_lng)
            self._coords = x, y

        return self._coords

    def subsection(self, x, y, zoom):
        self.load_file_data()

        ratio = self.sizes[zoom]
        tile_width = self.width*ratio
        num_tiles = int(1/ratio)

        x %= num_tiles
        y %= num_tiles

        min_x = int(tile_width*x)
        min_y = int(tile_width*y)
        max_x = int(min_x + tile_width)
        max_y = int(min_y + tile_width)
        return self.pixels[min_x:max_x, min_y:max_y]