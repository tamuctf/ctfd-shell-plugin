FROM ubuntu:latest

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y openssh-server
RUN apt-get install -y shellinabox curl tar docker
RUN curl -fsSLO https://get.docker.com/builds/Linux/x86_64/docker-1.13.1.tgz
RUN tar --strip-components=1 -xvzf docker-1.13.1.tgz -C /usr/local/bin

RUN mkdir /var/run/sshd

EXPOSE 31337
EXPOSE 4200

COPY add-user.sh /
COPY user-shell /usr/local/bin/user-shell
RUN sh -c "echo '/usr/local/bin/user-shell' >> /etc/shells"


