import ast
import base64
import statistics

import cv2
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

from utils import read_yaml, get_data, get_zoom, save_map_html, save_image, process_image


class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['wsgi.url_scheme'] = 'https'
        return self.app(environ, start_response)


app = Flask(__name__)
CORS(app)


# def run_request():
#     index = int(request.json['index'])
#     list = ['red', 'green', 'blue', 'yellow', 'black']
#     return list[index]
#
#
# @app.route('/', methods=['GET', 'POST'])
# def hello_world():
#     if request.method == 'GET':
#         return 'The model is up and running. Send a POST request'
#     else:
#         return run_request()


@app.route("/get_map_image/", methods=['POST'])
def get_map_image():
    """Full pipeline to get map image given kgs22"""
    kgs_number = request.json['kgs22']
    # kgs_number = request.args.get('kgs22', '')
    kgs_number = int(kgs_number)

    credentials = read_yaml('configs.yaml')
    data = get_data(kgs_number, credentials['DATABASE'])

    coordinates_dict = ast.literal_eval(data['rectangle'].values[0])
    coordinates = [list(i.values()) for i in coordinates_dict]

    avg_lat = statistics.mean([coordinate[0] for coordinate in coordinates])
    avg_lon = statistics.mean([coordinate[1] for coordinate in coordinates])

    coordinates.append(coordinates[0])

    zoom = get_zoom(data)

    html_file_name = 'example_map.html'
    image_file_name = 'map.png'

    save_map_html(avg_lat, avg_lon, zoom, coordinates, html_file_name)
    save_image(html_file_name, image_file_name)

    image = process_image(image_file_name)

    # Encode image to base64
    _, buffer = cv2.imencode('.jpg', np.array(image))
    jpg_as_text = base64.b64encode(buffer)

    response = jsonify(image=jpg_as_text.decode("utf-8"))
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=12000)  # host='0.0.0.0', port=80
