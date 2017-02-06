FROM ubuntu:latest

RUN apt-get update && apt-get install -y openssh-server
RUN apt-get install -y shellinabox

RUN mkdir /var/run/sshd

EXPOSE 31337
EXPOSE 4200

RUN shellinaboxd -b -t -p 4200
