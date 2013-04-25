#!/usr/bin/env python

import sys
import os
import cgi, cgitb
import json

import base64
import aes
from cloak.config import Config
from cloak.db import DB

def getUserPassword(usr):
	longpass = usr[2];
	if longpass[0] != '{':
		return longpass

	splitpass = longpass.partition('}')
	return splitpass[2]

#cgitb.enable()
sys.stderr = sys.stdout

print "Content-Type: text/html\n"

params = cgi.FieldStorage()
u = params.getvalue('u')
c = params.getvalue('c')
m = params.getvalue('m')
n = params.getvalue('n')

# Create new cloak service
cfg = Config()
db = DB(cfg)

# Get user password from database
usr = db.get_user_from_username(u)
if usr == False:
	print "INVALID USER"
	sys.exit(0)
password = getUserPassword(usr)

# Verifies password
decrypted = aes.decrypt( c, password, 256 )
if decrypted != m:
	print "AUTH ERR"
	sys.exit(0)

# Generates random session key and save to database
sessionkey = base64.b64encode( os.urandom(64) )
wid = db.insert_websession( usr[0], sessionkey )

# Send session key in JSON
js = json.dumps( {'k': sessionkey, 'n' : n, 'w' : wid} )
crypted = aes.encrypt( ('%04x'%len(js))+js, password, 256 )
#print crypted
sys.stdout.write(crypted)

