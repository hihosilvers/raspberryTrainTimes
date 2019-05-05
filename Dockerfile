FROM balenalib/raspberrypi3-alpine-python:3.7.2-build

# Enable OpenRC
ENV INITSYSTEM on
# RUN apk update && apk add make gcc

# pip install python deps from requirements.txt
# For caching until requirements.txt changes
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app
WORKDIR /usr/src/app

CMD ["bash","start.sh"]