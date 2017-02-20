#!/bin/bash

apt-get update

apt-get install -y docker

cp add-user.sh ../../docker/ssh-docker/
cp user-shell ../../docker/ssh-docker/

pushd ../docker/user-docker
    docker build -t user-image . -m 500M 
popd

pushd ../docker/ssh-docker
	docker build -t shell-image .
	docker create -it --name shell-server -p 4200:4200 -p 31337:31337 -v /var/run/docker.sock:/var/run/docker.sock shell-image
	docker start shell-server
	docker exec -d shell-server shellinaboxd -b -t -p 4200 &
	docker exec -d shell-server /usr/sbin/sshd -p 31337 &
	docker exec -d shell-server setfacl -m g:ctf-users:rw /var/run/docker.sock
popd
