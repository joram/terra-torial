#!/usr/bin/python
import math
from flask import Flask, render_template
from file_managers.geotiff import GeoData

app = Flask(__name__)

geotiffs = GeoData()
sizes = [1.0/math.pow(2, x) for x in range(0, 30)]


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/map/2d')
def map_2d():
    return render_template("map.html")


@app.route('/map/3d')
def map_3d():
    return render_template("webgl.html")


@app.route('/api/v0/tile/<x>_<y>_<zoom>.jpg')
@app.route('/api/v0/zoom/<zoom>/tile/<x>/<y>/jpg/')
def jpg_tile(x, y, zoom):
    return geotiffs.jpg_tile_response(x, y, zoom=int(zoom))


@app.route('/api/v0/tile/<x>_<y>_<zoom>.obj')
@app.route('/api/v0/zoom/<zoom>/tile/<x>/<y>/obj/')
def obj_tile(x, y, zoom):
    return geotiffs.obj_tile_response(x, y, zoom=int(zoom))


if __name__ == '__main__':
    app.debug = True
    app.run()
