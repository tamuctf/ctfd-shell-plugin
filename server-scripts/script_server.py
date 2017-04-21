from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import os
import subprocess

#https://docs.python.org/2/library/simplexmlrpcserver.html

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

server = SimpleXMLRPCServer(("localhost", 8000),
                            requestHandler=RequestHandler,
			    allow_none=True)

server.register_introspection_functions()

bad_chars = ['&', '|', '<', '>', '(', '"', '`', ')', "'", "$"]

def add_user_func(name, password):

	valid_pass = True
	valid_name = True

	for ch in bad_chars:		
		if ch in password:
			valid_pass = False
			break
		if ch in name:
			valid_pass = False
			break
	if valid_pass and valid_name:
		subprocess.call(["docker", "exec", "shell-server", "./add-user.sh", name , password])
	
def change_user_func(name, password):
	valid_pass = True
	valid_name = True

	for ch in bad_chars:		
		if ch in password:
			valid_pass = False
			break
		if ch in name:
			valid_pass = False
			break
	if valid_pass and valid_name:
		subprocess.call(["docker", "exec", "shell-server", "./change-user-pass.sh", name , password])

server.register_function(add_user_func, 'add_user')
server.register_function(change_user_func, 'change_user')

server.serve_forever()

