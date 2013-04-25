#!/usr/bin/env python

import cgi
import sys
import aes
import json
import base64

import cloak.alias
from cloak.config import Config
from cloak.db import DB

sys.stderr = sys.stdout
print "Content-Type: text/html\n"

params = cgi.FieldStorage()
r = base64.b64decode( params.getvalue('r') )
j1 = json.loads(r)

# Create new cloak service
cfg = Config()
db = DB(cfg)
cloak.alias.cfgdata = cfg

# Get user from database
usr = db.get_user_from_username(j1['user'])
if usr == False:
	print "ERR: INVALID USER"
	sys.exit(0)

# Get session key from database
sessionkey = db.get_websession(usr[0], j1['w'])[0]
if sessionkey == None:
	print "ERR: NO SESSION"
	sys.exit(0)

# Decrypt
p = aes.decrypt(j1['c'], sessionkey, 256)

# Load json string
j2 = json.loads(p)
j2keys = j2.keys()

alias = None
if 'alias' in j2keys:
	alias = j2['alias']

hint = None
if 'hint' in j2keys:
	hint = j2['hint']

# If alias is specified, get aid.
# Else, get last primary alias.
aid = None
uid = None
if alias != None and alias != "":
	result = db.get_aliasname_data(alias)
	if result[0] == None:
		# No such alias, create one as a primary alias
		uid = usr[0]
		aid = db.insert_alias(uid, alias, True )
	else:
		(aid, uid) = result
		if uid != usr[0]:
			print "ERR: WRONG ALIAS OWNER"
			sys.exit(0)
else:
	uid = usr[0]
	result = db.get_primary_alias(uid)
	if result == None:
		print "ERR: NO PRIMARY"
		sys.exit(0)

	(aid, alias) = result
	assert (alias != "")

# Generate random integer
rint = cloak.alias.generate_rint()

# Update database
db.insert_aliasrnd(uid, aid, alias, rint, 1, hint=hint, domain=j2['domain'])

# Return alias
#print alias+cfg.DEFAULTSEPARATOR+cloak.alias.rint_to_rstr(rint)
sys.stdout.write(alias+cfg.DEFAULTSEPARATOR+cloak.alias.rint_to_rstr(rint)+'@'+cfg.DOMAIN)
