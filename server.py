#!/usr/bin/python
import math
from flask import Flask, render_template, make_response
from file_managers.geotiff import GeoData
from views.tiles import get_tile_data

geotiffs = GeoData()
app = Flask(__name__)
app.debug = True
sizes = [1.0/math.pow(2, x) for x in range(0, 30)]

@app.route('/')
def index():
    return render_template("map.html")


@app.route('/tile/<x>_<y>_<zoom>.jpg')
@app.route('/tile/<x>/<y>/zoom/<zoom>/')
def tile(x, y, zoom):
    data = get_tile_data(x, y, int(zoom))
    if data:
        resp = make_response(data)
        resp.content_type = "image/jpeg"
        return resp
    return ""

if __name__ == '__main__':
    app.run()