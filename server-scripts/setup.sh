#!/bin/bash

apt-get update

apt-get install -y docker
apt-get install -y shellinaboxd

groupadd ctf-users

chmod +x user-shell

cp user-shell /usr/local/bin/user-shell
sh -c "echo '/usr/local/bin/user-shell' >> /etc/shells"

pushd ../docker/user-docker
    docker build -t user-image . -m 500M 
popd

pushd ../docker/ssh-docker
	docker build -t shell-image .
	docker create -it --name shell-server -p 4200:4200 -p 31337:31337 shell-image
	docker start shell-server
	docker exec -d shell-server shellinaboxd -b -t -p 4200 &
	docker exec -d shell-server /usr/sbin/sshd -p 31337 &
popd
