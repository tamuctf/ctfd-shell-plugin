#!/usr/bin/python

from subprocess import Popen, PIPE
import sys

user = sys.argv[1]
password = sys.argv[2]

#https://stackoverflow.com/questions/4688441/how-can-i-set-a-users-password-in-linux-from-a-python-script
proc=Popen(['passwd', user],stdin=PIPE,stdout=PIPE,stderr=PIPE) 
proc.stdin.write(password+'\n')
proc.stdin.write(password)
proc.stdin.flush()  
stdout,stderr = proc.communicate()

if stderr:
	print stderr
	print stdout


"""
echo -e "$PASS\n$PASS" | passwd "$USER"
"""