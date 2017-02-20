#!/bin/bash

groupadd docker
groupadd ctf-users
useradd -G ctf-users,docker -s /usr/local/bin/user-shell "$1"
echo -e "$1\n$1" | passwd "$1"

chsh -s /usr/local/bin/user-shell "$1"

docker create -it --name "$1" user-image /bin/bash

docker start "$1"
docker exec "$1" useradd -ms /bin/bash "$1"
docker stop "$1"

