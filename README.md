# CTFd-shell-plugin
Plugin for CTFd that integrates a web based shell  
*DISCLAIMER* This plugin is not complete and not guaranteed to be secure    
# Usage:  

##Plugin:
Copy shell-plugin directory into to the plugins directory of CTFd  
  
##setup.sh
Run to set up all of the environment tools this plugin needs  
  
##add-user.sh  
Script that takes a username as an argument, creates the user, changes the login shell of the user to user-shell, and creates a docker container for that user  
  
##user-shell  
A login script for users that you want to be directly logged into its corresponding docker container
