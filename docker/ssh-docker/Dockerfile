FROM ubuntu:latest

RUN apt-get update

RUN apt-get install -y openssh-server
RUN apt-get update
RUN apt-get install -y shellinabox curl tar acl git python-pip
RUN groupadd ctf-users
RUN groupadd docker

RUN curl -fsSLO https://get.docker.com/builds/Linux/x86_64/docker-1.13.1.tgz
RUN tar --strip-components=1 -xvzf docker-1.13.1.tgz -C /usr/local/bin

#RUN setfacl -m g:ctf-users:rw /var/run/docker.sock

RUN mkdir /var/run/sshd

EXPOSE 2222
EXPOSE 4200

COPY add_user.py /
COPY user_shell.py /usr/local/bin/user_shell.py
COPY change_user_pass.py / 

RUN chmod +x /add_user.py
RUN chmod +x /usr/local/bin/user_shell.py
RUN chmod +x /change_user_pass.py

RUN sh -c "echo '/usr/local/bin/user_shell.py' >> /etc/shells"


