# CTFd-shell-plugin
Plugin for CTFd that integrates a web based shell using docker containers.  

# Usage:  

## Configuration:  
There are a few manual configurations you will have to do in order to succesfully setup the plugin.  

### Apache:  
The web based shell is routed through an Apache web server with ssl enabled and then passed to the shellinabox container locally.  
In order to setup the Apache web server for your ctf you have to make a few changes.  
1. Add `ServerName www.example.com` and `ServerAlias example.com` with your url to the  
`docker/apache-docker/default-ssl.conf` file.  
2. Change `ProxyPass / http://192.168.1.68:4300/ ` and `ProxyPass /shell http://192.168.1.68:4300/` to the local/private address of your shell server.  
Note: `localhost` will not work as the address due to the web server being inside of a docker container.  
3. Replace `apache.crt` and `apache.key` with your own certificates.  

### Plugin:
The plugin files need a few changes in order for it to work properly for your ctf.  
1. In `ctfd-shell-plugin/shell-plugin/shell-templates/shell.html` change `src="https://shell.ctf.tamu.edu/shell/"` to the public address of your shell server.  
2. Replace `'localhost'` on line 27 in `ctfd-shell-plugin/shell-plugin/shell.py` with the local/private address of your shell server.  
3. Replace `'localhost'` on line 5 in `ctfd-shell-plugin/server-scripts/shell_queue_recv.py` with the local/private address of your shell server.  
4. Copy shell-plugin directory into to the plugins directory of CTFd  
  
### Setup  
The final configuration needed is to just build and launch the docker containers.  
Run `./setup.sh`  
