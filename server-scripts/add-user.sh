#!/bin/bash
#http://jonaskunze.com/restrict-user-to-its-own-container-using-docker/

USER=${1// /}
PASS=${2// /}

useradd -G ctf-users -s /usr/local/bin/user-shell "$USER"

echo -e "$PASS\n$PASS" | passwd "$USER"

chsh -s /usr/local/bin/user-shell "$USER"

docker build -t user-image --build-arg USER=$USER -f docker/user-docker/Dockerfile github.com/tamuctf/CTFd-shell-plugin 

docker create -it --name "$USER" -w /home/"$USER" --read-only -e TMOUT=300 -h tamuctf-shell --cpus=".5" --memory="500M" -v /home/"$USER" user-image /bin/bash

