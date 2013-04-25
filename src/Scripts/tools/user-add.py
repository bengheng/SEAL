#!/usr/bin/python

# Adds user to cloak database.

import sys
import getopt
import re
import sqlite3
import os
import hashlib
import socket
import traceback
import random
import string

def PrintUsage():
	print "Usage: %s -d<database> -u<user> -p<password> -a<PLAIN or PLAIN-MD5 or DIGEST-MD5> -f<forwarding address> [-r<user realm>] [-s<64-char salt>] [-k<64-char retrieval key>]" % sys.argv[0]
	sys.exit(0)

def IsValidEmail( email ):
	regex = re.compile("^.+@.+\..{2,3}$")
	if regex.search( email ) == None:
		return False
	return True

def IsValidDB( db ):
	if os.path.exists( db ) == False:
		print "Missing database file \"%s\"!" % db
		return False

	conn = sqlite3.connect( db )
	cur = conn.cursor()
	try:
		cur.execute( "PRAGMA integrity_check;" )
	except sqlite3.DatabaseError:
		print "Database fails integrity check!"
		cur.close()
		conn.close()
		return False
	
	cur.close()
	conn.close()

	return True

def IsValidUsername( usrname ):
	if len(usrname) > 64:
		print "Username is too long!"
		return False
	return True

def IsValidPassword( usrpwd ):
	return True

def IsValidAuthMech( authmech ):
	return ( (authmech == "PLAIN") or (authmech == "PLAIN-MD5") or (authmech == "DIGEST-MD5") )

# Extracted from http://stackoverflow.com/questions/2532053/validate-hostname-string-in-python
def IsValidHostname(hostname):
	if len(hostname) > 255:
		return False
	if hostname[-1:] == ".":
		hostname = hostname[:-1] # strip exactly one dot from the right, if present
	allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
	
	return all(allowed.match(x) for x in hostname.split("."))

def IsValidRealm( usrrealm ):
	print "Checking user realm \"%s\"..." % usrrealm
	return IsValidHostname( usrrealm )

def GetHashedPwd( usrname, realm, pwd ):
	s = "%s:%s:%s" % ( usrname, realm, pwd )
	print s
	return hashlib.md5( s ).hexdigest()	




# Adds user to database. The user password is stored
# in DIGEST-MD5 format.
def UserAdd( db, usrname, usrpwd, authmech, fwdaddr, salt, retrievalkey, usrrealm ):

	if authmech == "PLAIN":
		pwd = "{PLAIN}"+usrpwd	
	elif authmech == "DIGEST-MD5":
		pwd = "{DIGEST-MD5}"+GetHashedPwd( usrname, usrrealm, usrpwd )
	elif authmech == "PLAIN-MD5":
		# This is currently the preferred method.
		m = hashlib.md5()
		m.update( usrpwd )
		pwd = "{PLAIN-MD5}"+m.hexdigest()
	else:
		print "Cannot proceed! I've never seen authentication mechanism \"%s\" before!" % authmech
		sys.exit(1)

	conn = sqlite3.connect(db)

	cur = conn.cursor()
	try:
		# Checks if username is already in use.
		# This may not be very efficient.
		# TODO: Should we leave it to sqlite3
		# to do the checking via the unique
		# constraint and check for exception?
		cur.execute( "SELECT COUNT(*) FROM `user` " \
			"WHERE `username` = \"%s\";" % \
			usrname )

		nrow = cur.fetchone()[0]
		
		if nrow  == 0:
			cur.execute( "INSERT OR FAIL INTO `user` " \
				"(`username`, `spwd`, `fwdaddr`, `salt`, `retrievalkey`, `timecreated`) VALUES " \
				"(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", strftime(\'%%s\', \'now\'));" % \
				(usrname, pwd, fwdaddr, salt, retrievalkey) )
		else:
			print "User \"%s\" already exists in the database!\n" % usrname

			#
			# Update password and forwarding address
			#
			usrin = ""
			while usrin != "YES" and usrin != "no":
				usrin = raw_input( "Do you want to update the password and forwarding address? (YES/no) " )
				continue

			if usrin == "YES":
				cur.execute( "UPDATE `user` SET `spwd` = \"%s\", fwdaddr = \"%s\" " \
					"WHERE `username` = \"%s\";" % \
					( pwd, fwdaddr, usrname ) )

			#
			# Update salt
			#
			usrin = ""
			while usrin != "YES" and usrin != "no":
				usrin = raw_input( "Do you want to update the salt? (YES/no) " )
				continue

			if usrin == "YES":
				cur.execute( "UPDATE `user` SET `salt` = \"%s\" " \
					"WHERE `username` = \"%s\";" % \
					( salt, usrname ) )

			#
			# Update retrievalkey
			#
			usrin = ""
			while usrin != "YES" and usrin != "no":
				usrin = raw_input( "Do you want to update the retrieval key? (YES/no) " )
				continue

			if usrin == "YES":
				cur.execute( "UPDATE `user` SET `retrievalkey` = \"%s\" " \
					"WHERE `username` = \"%s\";" % \
					( retrievalkey, usrname ) )

	except sqlite3.DatabaseError:
		print "Unexpected database error:", sys.exc_info()[0]
		traceback.print_exc(file=sys.stdout)
	cur.close()

	conn.commit()
	conn.close()

optlist, args = getopt.getopt( sys.argv[1:], 'd:f:p:a:u:r:s:k:' )

db = ""
fwdaddr = ""
usrpwd = ""
usrname = ""
authmech = ""
salt = ""
retrievalkey = ""
usrrealm = socket.gethostbyaddr( socket.gethostname() )[0]

# Gets user options.
for opt in optlist:
	if opt[0] == '-d':
		db = os.path.realpath( opt[1] )
	elif opt[0] == '-f':
		fwdaddr = opt[1]
	elif opt[0] == '-p':
		usrpwd = opt[1]
	elif opt[0] == '-a':
		authmech = opt[1]
	elif opt[0] == '-s':
		salt = opt[1]
	elif opt[0] == '-k':
		retrievalkey = opt[1]
	elif opt[0] == '-u':
		usrname = opt[1]
	elif opt[0] == '-r':
		usrrealm = opt[1]
	else:
		print "Ignoring unknown option \"%s\"" % opt

#
# Sanity checks
#

if db == '' or fwdaddr == '' or usrpwd == '' or usrname == '':
	print "Missing arguments."
	PrintUsage()

if IsValidEmail( fwdaddr ) == False:
	print "Invalid forwarding address."
	PrintUsage()

if IsValidDB( db ) == False:
	print "Invalid SQLite3 database."
	PrintUsage()

if IsValidUsername( usrname ) == False:
	print "Invalid username."
	PrintUsage()

if IsValidPassword( usrpwd ) == False:
	print "Invalid password."
	PrintUsage()

if IsValidAuthMech( authmech ) == False:
	print "Invalid authentication mechanism \"%s\"." % authmech
	PrintUsage()

if IsValidRealm( usrrealm ) == False:
	print "Invalid user realm."
	PrintUsage()

#
# Done with sanity checks. Get to the job proper.
#

print "Database: %s" % db
print "User: %s" % usrname
print "Password: %s" % usrpwd
print "Auth Mechanism: %s" % authmech
print "Forwarding Address: %s" % fwdaddr
print "User Realm: %s" % usrrealm

if salt == "":
	salt = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(64))
	print "Generated Salt: %s" % salt
else:
	print "Salt: %s" % salt

if retrievalkey == "":
	retrievalkey = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(64))
	print "Generated Retrieval Key: %s" % retrievalkey
else:
	print "Retrieval Key: %s" % retrievalkey

UserAdd( db, usrname, usrpwd, authmech, fwdaddr, salt, retrievalkey, usrrealm )
