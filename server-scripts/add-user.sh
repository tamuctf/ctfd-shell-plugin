#!/bin/bash

useradd -G ctf-users -s /usr/local/bin/user-shell "$1"
echo -e "$2\n$2" | passwd "$1"

chsh -s /usr/local/bin/user-shell "$1"

docker create -it -w "/home/$1" --name "$1" -h tamuctf-shell user-image /bin/bash

docker start "$1"
docker exec "$1" useradd -ms /bin/bash "$1"
docker stop "$1"
