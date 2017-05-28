#!/usr/bin/python

import subprocess
from subprocess import Popen, PIPE
import sys

user = sys.argv[1]
password = sys.argv[2]

subprocess.call(["useradd", "-G", "ctf-users", "-s", "/usr/local/bin/user-shell", user])

#https://stackoverflow.com/questions/4688441/how-can-i-set-a-users-password-in-linux-from-a-python-script
proc=Popen(['passwd', user],stdin=PIPE,stdout=PIPE,stderr=PIPE) 
proc.stdin.write(password+'\n')
proc.stdin.write(password)
proc.stdin.flush()  
stdout,stderr = proc.communicate()

if stderr:
	print stderr
	print stdout

subprocess.call(["chsh", "-s", "/usr/local/bin/user_shell.py", user])

subprocess.call(["docker", "build", "-t", "user-image", "--build-arg", "USER="+user, "-f", "docker/user-docker/Dockerfile", "github.com/tamuctf/CTFd-shell-plugin"])

subprocess.call(["docker", "create", "-it", "--name", user, "-w", "/home/"+user, "--read-only", "-e", "TMOUT=86400", "-h", "tamuctf-shell", "-v", "/home/"+user, "user-image", "/bin/bash"])

"""
useradd -G ctf-users -s /usr/local/bin/user-shell "$USER"

echo -e "$PASS\n$PASS" | passwd "$USER"

chsh -s /usr/local/bin/user-shell "$USER"

docker build -t user-image --build-arg USER=$USER -f docker/user-docker/Dockerfile github.com/tamuctf/CTFd-shell-plugin 

docker create -it --name "$USER" -w /home/"$USER" --read-only -e TMOUT=300 -h tamuctf-shell --cpus=".5" --memory="500M" -v /home/"$USER" user-image /bin/bash
"""
