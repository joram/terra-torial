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

        # parse width, height, pixels from image
        im = tifffile.TiffFile(self.filepath)
        self.pixels = im.asarray()
        self.width = len(self.pixels)
        self.height = len(self.pixels[0])

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
        if not (self.min_lat <= lat <= self.max_lat):
            return False
        if not (self.min_lng <= lng <= self.max_lng):
            return False
        return True

    def coords_to_xy(self, lat, lng):
        if not self.contains(lat, lng):
            return None

        lat_ratio = abs(lat - self.min_lat)
        lng_ratio = abs(lng - self.min_lng)
        x = int(self.width*lat_ratio)
        y = int(self.height*lng_ratio)
        return x, y

    def subsection(self, min_coords, max_coords):
        x1, y1 = self.coords_to_xy(min_coords[0], min_coords[1])
        x2, y2 = self.coords_to_xy(max_coords[0], max_coords[1])
        return self.pixels[x1:x2, y1:y2]


class GeoData(object):

    def __init__(self):
        self.min_lat = None
        self.max_lat = None
        self.min_lng = None
        self.max_lng = None
        self.geo_tiffs = {}
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        data_dir = os.path.join(curr_dir, "../data/")
        for filename in os.listdir(data_dir):
            filepath = os.path.join(data_dir, filename)
            if os.path.isfile(filepath):
                self.add_geo_tiff(filepath)

    def add_geo_tiff(self, filepath):
        geo_tiff = GeoTiff(filepath)
        self.geo_tiffs[(geo_tiff.min_lat, geo_tiff.min_lng)] = geo_tiff
        self.min_lat = min(self.min_lat, geo_tiff.min_lat) if self.min_lat else geo_tiff.min_lat
        self.max_lat = max(self.max_lat, geo_tiff.max_lat) if self.max_lat else geo_tiff.max_lat
        self.min_lng = min(self.min_lng, geo_tiff.min_lng) if self.min_lng else geo_tiff.min_lng
        self.max_lng = max(self.max_lng, geo_tiff.max_lng) if self.max_lng else geo_tiff.max_lng

    def key(self, lat, lng):
        min_lat = int(math.floor(lat))
        min_lng = int(math.floor(lng))
        return min_lat, min_lng

    def exists(self, lat, lng):
        if self.key(lat, lng) in self.geo_tiffs.keys():
            return True
        return False

    def heightmap(self, min_coords, max_coords):
        min_lat, min_lng = min_coords
        if self.exists(min_lat, min_lng):
            return self.geo_tiffs[self.key(min_lat, min_lng)].subsection(min_coords, max_coords)


    def get_heightmap(self, x, y, offset_x=48, offset_y=-123, zoom=0):
        sizes = [1.0/math.pow(2, s) for s in range(0, 30)]
        size = sizes[zoom]
        lat = offset_x + float(y)*size
        lng = offset_y + float(x)*size

        if not self.exists(lat, lng):
            return None

        min_coords = (lat, lng)
        max_coords = (lat+size, lng+size)
        return self.heightmap(min_coords, max_coords)

    def jpg_tile_response(self, x, y, offset_x=48, offset_y=-123, zoom=0):
        data = self.get_heightmap(x, y, offset_x, offset_y, zoom)
        if not data.any():
            return None

        img = Heightmap(data).get_jpg()
        output = io.BytesIO()
        img.save(output, format="JPEG")
        resp = make_response(output.getvalue())
        resp.content_type = "image/jpeg"
        return resp

    def obj_tile_response(self, x, y, offset_x=48, offset_y=-123, zoom=0):
        data = self.get_heightmap(x, y, offset_x, offset_y, zoom)
        if not data.any():
            return None

        obj_str = Heightmap(data).get_obj()
        output = io.BytesIO()
        output.writelines(obj_str)
        resp = make_response(output.getvalue())
        resp.content_type = "object/wavefront"
        return resp
