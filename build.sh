#!/bin/bash

VER=`cat __init__.py | grep __version__ | awk -F '=' '{print $2}' | sed 's/ //g' | sed 's/"//g'`

REGISTRY='registry.example.ru'
IMAGE_NAME='duty-board'

docker build --tag $REGISTRY/$IMAGE_NAME:$VER .
docker push $REGISTRY/$IMAGE_NAME:$VER
