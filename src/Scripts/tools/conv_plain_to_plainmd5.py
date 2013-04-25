#!/usr/bin/env python

# This utility script converts dovecot compatible PLAIN passwords to PLAIN-MD5

import os
import sys
import sqlite3
import string
import getopt
import hashlib
from inspect import currentframe

def PrintUsage():
	print "Usage: %s -d<database>" % sys.argv[0]
	sys.exit(0)

optlist, args = getopt.getopt( sys.argv[1:], 'd:' )

db = ""

for opt in optlist:
	if opt[0] == '-d':
		db = os.path.realpath( opt[1] )

if db == "":
	print "Missing database location."
	PrintUsage()

if os.path.exists( db ) == False:
	print "Missing database file \"%s\"!" % db
	sys.exit(0)


# Database integrity check
conn = sqlite3.connect( db )
cur = conn.cursor()
try:
	cur.execute( "PRAGMA integrity_check;" )
except sqlite3.DatabaseError:
	print "Database fails integrity check!"
	cur.close()
	conn.close()
	sys.exit(0)
cur.close()
conn.close()


# For every user, replace PLAIN password
conn = sqlite3.connect( db )
cur = conn.cursor()
n = 0
try:
	cur.execute( "SELECT uid, spwd FROM user" )
	row = cur.fetchone()
	while row:
		uid = row[0]
		curpwd = row[1]

		# Check if password begins with "{PLAIN}"
		if string.find( curpwd, '{PLAIN}' ) != 0:
			row = cur.fetchone()
			continue

		orgpwd = curpwd[len('{PLAIN}'):]
		m = hashlib.md5()
		m.update(orgpwd)
		newpwd = "{PLAIN-MD5}"+m.hexdigest()

		ucur = conn.cursor()
		ucur.execute( "UPDATE user SET spwd=? WHERE uid=?", (newpwd, uid,) )
		conn.commit()
		ucur.close()
		
		n = n + 1
		row = cur.fetchone()
except sqlite3.Error, e:
	logging.fatal('%s:%d\t%s',			\
		currentframe().f_code.co_filename,	\
		currentframe().f_lineno,		\
		e.args[0])

cur.close()
conn.close()

print "Converted %d PLAIN passwords to PLAIN-MD5." % n
