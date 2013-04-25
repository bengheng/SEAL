#!/usr/bin/python

import os
import re
import sys
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import string
import random
import hashlib
import sqlite3
import traceback
import subprocess

#sys.stderr = sys.stdout
#print "Content-Type: text/plain\n\n"
#print "test"
#print_html('test')


VERIFYPASS = "ka0lc-ht1mS"

form = cgi.FieldStorage()
accountname = form.getvalue("username", None)
accountname = accountname.lower() if accountname else None

password = form.getvalue("passwd", None)
password2 = form.getvalue("passwdagain", None)

fwdaddx = form.getvalue("fwdaddx", None)
fwdaddx = fwdaddx.lower() if fwdaddx else None

verify = form.getvalue("passverify", None)

def print_prologue():
	print "Content-Type: text/html\n\n"
	sys.stdout.write( '<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\">' )
	sys.stdout.write( '<html>\n' )
	
	sys.stdout.write( '<head>\n' )
	sys.stdout.write( '<meta http-equiv="Content-Type" content="text/html; charset=us-ascii">\n' )
	sys.stdout.write( '<title>SEAL - Account Creation</title>\n' )
	sys.stdout.write( '<link rel="stylesheet" type="text/css" href="/style.css" media="screen">\n' )
	sys.stdout.write( '</head>\n' )

	sys.stdout.write( '<body>\n' )
	sys.stdout.write( '<div id="wrap">\n' )
	sys.stdout.write( '<div id="top"></div>\n' )
	sys.stdout.write( '<div id="content">\n' )

	sys.stdout.write( '<div class="header">\n' )
	sys.stdout.write( '<h1><a href="/index.php">SEAL</a></h1>\n' )
	sys.stdout.write( '<h2>Account Creation</h2>\n' )
	sys.stdout.write( '</div>\n' )

	sys.stdout.write( '<div class="breadcrumbs">\n' )
	sys.stdout.write( '<a href="/index.php">Home</a> &middot; <a href="/adduser.php">Register</a>\n' )
	sys.stdout.write( '</div>\n' )

	sys.stdout.write( '<div class="middle">\n' )

def print_epilogue():
	sys.stdout.write( '</div>\n' )

	sys.stdout.write( '<div id="clear"></div>\n' )
	sys.stdout.write( '</div>\n' )
	sys.stdout.write( '<div id="bottom"></div>\n' )
	sys.stdout.write( '</div>\n' )

	sys.stdout.write( '<div id="footer">\n' )
	sys.stdout.write( '<font size="-1" color="#666666">&copy;2011 - University of Michigan</font>\n' )
	sys.stdout.write( '</div>\n' )
	sys.stdout.write( '</body>\n' )

	sys.stdout.write( '</html>\n' )


def accountname_exists( conn, accountname ):
	cur = conn.cursor()
	row = None
	try:
		cur.execute( 'SELECT COUNT(*) FROM user WHERE username=?', (accountname,) )
		row = cur.fetchone()
	except sqlite3.DatabaseError:
		print 'Unexpected database error: ', sys.exc_info()[0]
		traceback.print_exc(file=sys.stdout)
	cur.close()
	return row[0] != 0


def is_valid_email( email ):
        regex = re.compile("^.+@.+\..{2,3}$")
        if regex.search( email ) == None:
                return False
        return True


def add_user( conn, usrname, pwd, fwdaddr, salt, retrievalkey ):
	cur = conn.cursor()

	try:
		cur.execute( "INSERT OR FAIL INTO `user` " \
			"(`username`, `spwd`, `fwdaddr`, `salt`, `retrievalkey`, `timecreated`) VALUES " \
            "(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", strftime(\'%%s\', \'now\'));" % \
            (usrname, pwd, fwdaddr, salt, retrievalkey) )
		conn.commit()
	except sqlite3.DatabaseError:
		print 'Unexpected database error: ', sys.exc_info()[0]
		traceback.print_exc(file=sys.stdout)

	cur.close()


print_prologue()
conn = sqlite3.connect( '/home/john/cloak/data/cloakdb' )
err = ''

if not accountname:
	err += '<li>Missing account name.</li>\n'
elif accountname_exists( conn, accountname ) == True:
	err += '<li>Account Name already taken.</li>'
if not password:
	err += '<li>Missing password.</li>\n'
elif len(password) < 8:
	err += '<li>Password must have at least 8 characters.</li>'
if not password2:
	err += '<li>Did not retype password.</li>\n'
if password and password2 and password != password2:
	err += '<li>Passwords did not match.</li>\n'
if not fwdaddx:
	err += '<li>Missing forwarding email address.</li>\n'
elif is_valid_email( fwdaddx ) == False:
	err += '<li>Invalid forwarding email address.</li>'
if not verify:
	err += '<li>Missing verification password.</li>\n'
elif verify != VERIFYPASS:
	err += '<li>Bad verification password.</li>\n'

if err == '':
	# Prepare password
	m = hashlib.md5()
	m.update( password )
	hashedpwd = '{PLAIN-MD5}'+m.hexdigest()

	# User realm
	# usrrealm = socket.gethostbyaddr( socket.gethostname() )[0]

	# Salt
	salt = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(64))

	# Retrieval key
	retrievalkey = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(64))

	add_user( conn, accountname, hashedpwd, fwdaddx, salt, retrievalkey )
	print 'Account created successfully.<br>'
	print '<b>Remember to log in to your SEAL account and create SEAL alias '\
		'for distribution to your contacts.</b>'

else:
	print 'The following error(s) occurred while creating your account.<br>\n'
	print '<ul>\n'
	print err
	print '</ul>\n'

conn.close()
print_epilogue()
