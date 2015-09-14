import io
import json
import math
import os
from file_managers.heightmap import Heightmap
from flask import make_response
from file_managers.geotiff import GeoTiff


class GeoData(object):

    def __init__(self):
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
        self.geo_tiffs[geo_tiff.coords] = geo_tiff

    def heightmap(self, x, y, zoom):
        ratio = self.sizes[zoom]
        coords = (math.floor(x*ratio), math.floor(y*ratio))
        geo_tiff = self.geo_tiffs.get(coords)
        if geo_tiff:
            return geo_tiff.subsection(y, x, zoom)

    def jpg_tile_response(self, x, y, zoom=0, size=256):
        data = self.heightmap(x, y, zoom)
        if data == None or not data.any():
            return None

        img = Heightmap(data, resize=(size, size)).get_jpg()
        output = io.BytesIO()
        img.save(output, format="JPEG")
        resp = make_response(output.getvalue())
        resp.content_type = "image/jpeg"
        return resp

    def heightmap_tile_response(self, x, y, zoom=0, size=256):
        data = self.heightmap(x, y, zoom)
        if data == None or not data.any():
            return None

        matrix = Heightmap(data, resize=(size, size)).get_matrix()
        return make_response(json.dumps(matrix))