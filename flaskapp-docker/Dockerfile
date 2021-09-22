# syntax=docker/dockerfile:1

FROM python:3.6

## Installing Chrome
# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Adding Google Chrome to the repositories
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Updating apt to see and install Google Chrome
RUN apt-get -y update

# Magic happens
RUN apt-get install -y google-chrome-stable

## Installing driver
# Installing Unzip
RUN apt-get install -yqq unzip

# Download the Chrome Driver
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip

# Dependencies for cv2 package
RUN apt-get install ffmpeg libsm6 libxext6  -y

# Install required packages
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

# Copy app files
COPY flaskapp /app/

# Set working directory
WORKDIR /app

# Unzip the Chrome Driver into /usr/local/bin directory
RUN unzip /tmp/chromedriver.zip chromedriver -d /app

# Set display port as an environment variable
ENV DISPLAY=:99

# RUN apt-get update

# RUN apt-get install gunicorn3 -y

CMD [ "gunicorn", "-b", "0.0.0.0:12000", "wsgi:server", "--workers=3"]
# CMD [ "python3", "app.py"]