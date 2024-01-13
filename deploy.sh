#!bin/bash

cd dev/music-bot/
echo $DOCKER_PASSWORD | sudo docker login --password-stdin --username $DOCKER_USER
sudo docker pull $DOCKER_USER/$DOCKER_REPO:main
sudo docker run -d $DOCKER_USER/$DOCKER_REPO:main
