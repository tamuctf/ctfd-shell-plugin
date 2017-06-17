#!/bin/bash

set -euo pipefail

sudo apt-get update

sudo apt-get install -y docker.io python-pip rabbitmq-server

cp server-scripts/add_user.py docker/ssh-docker/
cp server-scripts/user_shell.py docker/ssh-docker/
cp server-scripts/change_user_pass.py docker/ssh-docker

pushd docker/ssh-docker
	docker build -t shell-image .
	docker create -it --name shell-server -h tamuctf-shell -p 4300:4300 -p 2222:2222 -v /dev/fuse:/dev/fuse -v /var/run/docker.sock:/var/run/docker.sock shell-image
	docker start shell-server
	docker exec -d shell-server shellinaboxd -b -t -p 4300 &
	docker exec -d shell-server /usr/sbin/sshd -p 2222 &
	docker exec -d shell-server setfacl -m g:ctf-users:rw /var/run/docker.sock
popd

pushd docker/apache-docker
	docker build -t apache-image .
	docker run -itd --name apache-server -p 80:80 -p 443:443 apache-image
popd

docker run -d --hostname shell-rabbit --name rabbit-server -p 5672:5672 -p 15672:15672 rabbitmq:latest

pushd server-scripts/
	python shell_queue_recv.py &> rabbitmqlog.txt &
popd
