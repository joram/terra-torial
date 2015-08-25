#!/usr/bin/python
from flask import Flask, render_template, redirect

from views.tiles import get_tile

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    return render_template("map.html")


@app.route('/tile/<x>/<y>/zoom/<zoom>/')
def tile(x, y, zoom):
    return redirect(get_tile(x, y, int(zoom)))

if __name__ == '__main__':
    app.run()