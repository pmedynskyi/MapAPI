import base64

import cv2
import requests
import numpy as np
import matplotlib.pyplot as plt


def test(inp):
    # server = 'http://34.240.222.177:12000'
    server = 'http://0.0.0.0:12000'
    response = requests.post(server + f'/get_map_image?kgs22={inp}')
    print(response.ok)

    response = response.json()

    image_base64 = response['image']
    jpg_original = base64.b64decode(image_base64)
    image_orig = cv2.imdecode(np.frombuffer(jpg_original, np.uint8), -1)

    plt.imshow(image_orig)
    plt.imsave('output_new.jpg', image_orig)
    plt.show()


if __name__ == "__main__":
    inp = '9162000000001'
    test(inp)
