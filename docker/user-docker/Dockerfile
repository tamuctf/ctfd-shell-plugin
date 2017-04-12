FROM ubuntu:latest

RUN dpkg --add-architecture i386

RUN apt-get update
RUN apt-get install -y\
	netcat\
	gdb\
	g++\
	radare2\
	nmap\
	telnet\
	vim\
	binutils-multiarch \
	coreutils\
	testdisk\
	exif\
	strace\
	ltrace\
	nano\
	dnsutils\
	iputils-ping\
	curl\
	wget\
	libc6:i386\
	libncurses5:i386\
	libstdc++6:i386\
	multiarch-support\
	python-pip

ARG USER 
RUN useradd -ms /bin/bash $USER	
