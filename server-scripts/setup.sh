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
	docker create -it --name shell-server shell-image
	docker start shell-servershell-server
	docker exec shell-server /usr/sbin/sshd -p 31337
popd
