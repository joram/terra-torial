import os
from geopy.geocoders import Nominatim
import tifffile
import math


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
        print "filepath:%s\t w:%s, h:%s\t lat:%s, lng:%s" % (
            self.filepath,
            self.width,
            self.height,
            self.min_lat,
            self.min_lng)

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

    def height_at(self, lat, lng):

        if not (self.min_lat <= lat <= self.max_lat):
            return None
        if not (self.min_lng <= lng <= self.max_lng):
            return None

        lat_ratio = abs(lat - math.floor(lat))
        lng_ratio = abs(lng - math.floor(lng))
        x = int(self.width*lat_ratio)
        y = int(self.height*lng_ratio)

        return self.pixels[x][y]


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

    def height(self, lat, lng):
        geo_tiff = self.geo_tiffs.get(self.key(lat, lng))
        return geo_tiff.height_at(lat, lng) if geo_tiff else 0

    def heights(self, min_lat, min_lng, max_lat, max_lng, resolution=0.001):
        latitudes = [min_lat + lat_tick*resolution for lat_tick in range(0, int((max_lat-min_lat)/resolution))]
        longitudes = [min_lng + lng_tick*resolution for lng_tick in range(0, int((max_lng-min_lng)/resolution))]
        data = []
        for lat in latitudes:
            row = [self.height(lat, lng) for lng in longitudes]
            data.append(row)
        return data

    def tiles(self, size=0.01, resolution=0.001, max=None):
        count = 0
        lat = self.min_lat
        lng = self.min_lng
        while lat < self.max_lat:
            while lng < self.max_lng:
                if max and count >= max:
                    return
                yield self.heights(lat, lng, lat+size, lng+size, resolution), lat, lng
                count += 1
                lng += size
            lat += size




# geo_data = GeoData()
#
# # import pprint
# tiles_count = 0
# for tile, lat, lng in geo_data.tiles(size=2, resolution=0.0025):
#     # pprint.pprint(tile)
#     write_obj(tile, "./test_%s_%s.obj" % (lat, lng))
#     tiles_count += 1
