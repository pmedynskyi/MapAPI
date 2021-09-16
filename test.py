import base64

import io
import requests
from PIL import Image
import matplotlib.pyplot as plt


def test(inp):
    server = 'https://localhost:12000'
    # server = 'http://34.240.222.177:12000'
    response = requests.post(server + f'/get_map_image?kgs22={inp}',
                             verify='cert.pem')
    print(response.ok)

    response = response.json()

    image_base64 = response['image']
    with open('base64.txt', 'w') as f:
        f.write(image_base64)
    # print(image_base64)
    jpg_original = base64.b64decode(image_base64)
    # image_orig = cv2.imdecode(np.frombuffer(jpg_original, np.uint8), -1)

    # Take in base64 string and return cv image
    image_orig = Image.open(io.BytesIO(jpg_original))
    # image_orig = cv2.cvtColor(np.array(image_orig), cv2.COLOR_BGR2RGB)

    plt.imshow(image_orig)
    # plt.imsave('output_new.jpg', image_orig)
    plt.show()


if __name__ == "__main__":
    inp = '2000000001524'
    test(inp)
