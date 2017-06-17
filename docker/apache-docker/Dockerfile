FROM ubuntu:latest

RUN apt-get update

RUN apt-get install -y apache2

RUN mkdir /etc/apache2/ssl

COPY ./index.html /var/www/html/index.html
COPY ./apache2.conf /etc/apache2/apache2.conf
COPY ./apache.crt /etc/apache2/ssl
COPY ./apache.key /etc/apache2/ssl
COPY ./default-ssl.conf /etc/apache2/sites-available/default-ssl.conf

EXPOSE 80
EXPOSE 443

RUN a2enmod ssl
RUN a2ensite default-ssl
RUN a2enmod proxy
RUN a2enmod proxy_http
RUN service apache2 restart


CMD ["apachectl", "-D", "FOREGROUND"]