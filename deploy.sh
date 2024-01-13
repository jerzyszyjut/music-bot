#!bin/bash

cd dev/music-bot/
sudo docker pull $DOCKER_USER/$DOCKER_REPO:main
sudo docker run -d $DOCKER_USER/$DOCKER_REPO:main
