#!/usr/bin/python

import subprocess

p = subprocess.Popen("whoami", stdin=subprocess.PIPE,stdout=subprocess.PIPE)
user, err = p.communicate()

#returns with \n attached
container_name = user[:-1]

subprocess.call(["docker", "start", container_name])

subprocess.call(["docker", "exec", "-it", "-u", container_name, container_name, "/bin/bash"])

subprocess.call(["docker", "stop", container_name])

"""
#!/bin/bash
container_name=`whoami`
docker start "$container_name"
docker exec -it -u "$container_name" "$container_name" /bin/bash
docker stop "$container_name"
"""