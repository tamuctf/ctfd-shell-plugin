FROM ubuntu:latest

RUN apt-get update && apt-get install -y\
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
	sudo\	
	python-pip

ARG USER 
RUN useradd -ms /bin/bash USER	
