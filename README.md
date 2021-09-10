# MapAPI
Flask API for map image generation

App works in **docker** container.
To install docker, please, follow [installation guide](https://docs.docker.com/engine/install/)

Docker image downloads all required Python packages and Chrome and chromdriver for Selenium.

## Usage
## Configs
Please add DB credential to **configs.yaml** prior to running the app.

### Docker Container
To create docker image, run the command:

```bash
docker build --tag python-docker .
```

To run docker container, execute the command:

```bash
docker run -p 12000:12000 python-docker
```

### Request

To get the image for particular kgs22 number, POST request should be send to following endpoint: 

`
http://{server_ip}:12000/get_map_image?kgs22={kgs22_number}
`

Where: 

**server_ip** - ip of the server where container is running
 
**kgs22_number** - requested kgs22 number

## Output

The returned object is JSON in following format:

```json
{
'image':  base64_encoded_image
}
```

Where: 

**base64_encoded_image** - resulting image for kgs22 number encoded in base64 format.