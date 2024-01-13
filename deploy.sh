#!bin/bash

cd dev/music-bot/
sudo docker pull $DOCKER_USER/$DOCKER_REPO:main
sudo docker stop $(sudo docker ps -a -q)
sudo docker rm $(sudo docker ps -a -q)
echo "sudo docker run -d $DOCKER_USER/$DOCKER_REPO:main"
sudo docker run -d $DOCKER_USER/$DOCKER_REPO:main
