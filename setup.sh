#!/bin/bash

set -euo pipefail

sudo apt-get update

sudo apt-get install -y docker.io python-pip

cp server-scripts/add_user.py docker/ssh-docker/
cp server-scripts/user_shell.py docker/ssh-docker/
cp server-scripts/change_user_pass.py docker/ssh-docker

pushd docker/user-docker
    docker build -t user-image --build-arg USER="test" -f docker/user-docker/Dockerfile github.com/tamuctf/CTFd-shell-plugin
popd

pushd docker/ssh-docker
	docker build -t shell-image .
	docker create -it --name shell-server -h tamuctf-shell -p 4300:4300 -p 2222:2222 -v /dev/fuse:/dev/fuse -v /var/run/docker.sock:/var/run/docker.sock shell-image
	docker start shell-server
	docker exec -d shell-server shellinaboxd -b -t -p 4300 &
	docker exec -d shell-server /usr/sbin/sshd -p 2222 &
	docker exec -d shell-server setfacl -m g:ctf-users:rw /var/run/docker.sock
popd

pushd server-scripts/
	python script_server.py &> xmlrpc_log.txt &
popd
