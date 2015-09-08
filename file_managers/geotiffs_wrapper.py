import io
import os
import math
from file_managers.heightmap import Heightmap
from flask import make_response
from file_managers.geotiff import GeoTiff


class GeoData(object):

    def __init__(self):
        self.min_lat = None
        self.max_lat = None
        self.min_lng = None
        self.max_lng = None
        self.geo_tiffs = {}
        self.sizes = [1.0/math.pow(2, s) for s in range(0, 30)]
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

    def heightmap(self, x, y, zoom):
        offset_lat = 48
        offset_lng = -123
        size = self.sizes[zoom]
        y += 1
        lat = offset_lat - float(y)*size
        lng = offset_lng + float(x)*size

        geo_tiff = self.geo_tiffs.get(self.key(lat, lng))
        if geo_tiff:
            return geo_tiff.subsection(x, y, zoom)

    def jpg_tile_response(self, x, y, zoom=0):
        data = self.heightmap(x, y, zoom)
        if data == None or not data.any():
            return None

        img = Heightmap(data).get_jpg()
        output = io.BytesIO()
        img.save(output, format="JPEG")
        resp = make_response(output.getvalue())
        resp.content_type = "image/jpeg"
        return resp

    def obj_tile_response(self, x, y, offset_x=48, offset_y=-123, zoom=0):
        data = self.get_heightmap(x, y, offset_x, offset_y, zoom)
        if data == None or not data.any():
            return None

        obj_str = Heightmap(data).get_obj()
        output = io.BytesIO()
        output.writelines(obj_str)
        resp = make_response(output.getvalue())
        resp.content_type = "object/wavefront"
        return resp
