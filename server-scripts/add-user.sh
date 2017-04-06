#!/bin/bash
#http://jonaskunze.com/restrict-user-to-its-own-container-using-docker/

useradd -G ctf-users -s /usr/local/bin/user-shell "$1"
echo -e "$2\n$2" | passwd "$1"

chsh -s /usr/local/bin/user-shell "$1"

docker build -t user-image --build-arg USER="$1" -f docker/user-docker/Dockerfile github.com/tamuctf/CTFd-shell-plugin 

docker create -it --name "$1" -w /home/"$1" --read-only -e TMOUT=300 -h tamuctf-shell --cpus=".5" --memory="500M" user-image /bin/bash

#docker start "$1"
#docker exec "$1" useradd -ms /bin/bash "$1"
#docker stop "$1"
