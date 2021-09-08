import os
import ast
import time
import base64
import statistics

import cv2
import folium
import pymysql
import numpy as np
import pandas as pd
from PIL import Image
from selenium import webdriver
from flask import Flask, request, jsonify
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)


def flatten(coordinates_list: list) -> list:
    """Flattens all values in list to one dimension"""
    flattened_list = []
    for coordinate in coordinates_list:
        if isinstance(coordinate, list):
            flattened_list.extend(flatten(coordinate))
        else:
            flattened_list.append(coordinate)
    return flattened_list


def get_data(kgs):
    """Get data from SQL server for given KGS22"""
    main_query = f"""
                    SELECT rectangle, radius
                    FROM 
                        `kgs22_coordinates`
                    WHERE 
                        `KGS22` = {kgs}
                    """

    conn = pymysql.connect(host="development-db-cluster.cs4heffb1ufh.eu-west-1.rds.amazonaws.com", user="dbadmin",
                           port=3306, passwd="6EH584R6R4ZNHT6", db="fcrimmo_db", connect_timeout=100000)
    df = pd.read_sql(main_query, conn)
    conn.close()
    return df


def get_zoom(df: pd.DataFrame) -> int:
    """Get zoom based on radius"""
    if 0 <= df['radius'][0] <= 0.2:
        zoom = 22
    elif 0.2 < df['radius'][0] <= 0.22:
        zoom = 18
    elif 0.22 < df['radius'][0] <= 0.5:
        zoom = 16
    elif 0.5 < df['radius'][0] <= 1.5:
        zoom = 15
    elif 1.5 < df['radius'][0] <= 3.3:
        zoom = 14
    elif 3.3 < df['radius'][0] <= 7:
        zoom = 13
    elif 7 < df['radius'][0] <= 10:
        zoom = 12
    elif 10 < df['radius'][0] <= 25:
        zoom = 11
    elif 25 < df['radius'][0] <= 50:
        zoom = 10
    elif 50 < df['radius'][0] <= 90:
        zoom = 9
    elif 90 < df['radius'][0] <= 170:
        zoom = 8
    elif 170 < df['radius'][0] <= 340:
        zoom = 7
    else:
        zoom = 6
    return zoom


def save_map_html(average_latitude: float, average_longitude: float, zoom_value: int,
                  coordinates_list: list, save_path: str) -> None:
    """Saves whole map with needed rectangle placed in HTML file"""
    my_map = folium.Map(location=[average_latitude, average_longitude], zoom_start=zoom_value,
                        tiles="https://{s}.tile.thunderforest.com/transport-dark/{z}/{x}/{"
                              "y}.png?apikey=01db46bcfb264fd08e937181b26b07f0",
                        attr='<a href="http://www.thunderforest.com/">Thunderforest</a>')

    folium.PolyLine(coordinates_list, color="red", weight=2.5, opacity=1).add_to(my_map)

    my_map.save(save_path)


def save_image(html_path: str, image_file_path: str) -> None:
    """Opens HTML file locally using headless Selenium and saves the screenshot"""
    options = Options()
    options.add_argument("--headless")

    tmpurl = 'file://{path}/{mapfile}'.format(path=os.getcwd(), mapfile=html_path)

    browser = webdriver.Chrome(executable_path='../Scraping/chromedriver', options=options)
    browser.get(tmpurl)
    time.sleep(2)
    browser.save_screenshot(image_file_path)
    browser.quit()


def process_image(image_file_path: str) -> Image:
    """Processes saved image"""
    im = Image.open(image_file_path)
    im = im.convert('RGBA')
    data = np.array(im)
    red, green, blue, alpha = data.T
    purple_areas = (red == 70) & (blue == 68) & (green == 49)
    light_purple_areas = (red == 100) & (blue == 100) & (green == 84)
    data[..., :-1][purple_areas.T] = (64, 64, 64)
    data[..., :-1][light_purple_areas.T] = (64, 64, 64)
    im2 = Image.fromarray(data)
    return im2, data


@app.route("/get_map_image/", methods=['POST'])
def get_map_image():
    """Full pipeline to get map image given kgs22"""
    kgs_number = request.args.get('kgs22', '')
    kgs_number = int(kgs_number)

    data = get_data(kgs_number)

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

    image, image_array = process_image(image_file_name)

    # Encode image to base64
    _, buffer = cv2.imencode('.jpg', image_array)
    jpg_as_text = base64.b64encode(buffer)

    return jsonify(image=jpg_as_text.decode("utf-8"))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=12000)
