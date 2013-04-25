#!/usr/bin/python

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import Message

from string import Template
import os
import re
import sys
import cgi
import socket
import string
import random
import hashlib
import sqlite3
import sendmail
import traceback
import subprocess

subject = 'SEAL Username/Password Reminder'

textversion = """

You have requested your SEAL username. A new password has also been generated.
Please change the password after logging in.

Username: $username
Password: $password

"""

htmlversion = """

<html>
<body>

You have requested your SEAL username. A new password has also been generated.
Please change the password after logging in.<br><br>

Username: $username<br>
Password: $password<br>

</body>
</html>

"""

username = sys.argv[1]

def reset_password(conn, username):
	# Generate password
	tmppassword = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(8))
	md5password = '{PLAIN-MD5}'+hashlib.md5(tmppassword).hexdigest()

	cur = conn.cursor()

	try:
		cur.execute('UPDATE user SET spwd=? WHERE username=?', (md5password, username,));
		if cur.rowcount < 1:
			cur.close()
			return None

		conn.commit()

	except sqlite3.DatabaseError:
		print 'Unexpected database error: ', sys.exc_info()[0]
		traceback.print_exc(file=sys.stdout)

	cur.close()
	return tmppassword

def get_fwdaddx(conn, username):
   	cur = conn.cursor()
	row = None

	try:
		cur.execute('SELECT fwdaddr FROM user WHERE username=?', (username,));
		row = cur.fetchone()

	except sqlite3.DatabaseError:
		print 'Unexpected database error: ', sys.exc_info()[0]
		traceback.print_exc(file=sys.stdout)

	cur.close()
	if row is None:
		return None

	return row[0]

conn = sqlite3.connect( '/home/john/cloak/data/cloakdb' )
err = ''

fwdaddx = get_fwdaddx(conn, username)
if fwdaddx == None:
	print 'Cannot find username \"'+username+"\"."
else:
	password = reset_password(conn, username)

	mailfrom = 'noreply@'+socket.getfqdn()
	msgtxt = Template(textversion).safe_substitute({'username':username, 'password':password})
	msghtml = Template(htmlversion).safe_substitute({'username':username, 'password':password})
	sendmail.sendmail_htmlmultipart(mailfrom, [fwdaddx], subject, msgtxt, msghtml)

	print 'A reminder email has been sent to your forwarding address. '
	print 'Please change your password as soon as possible.'

conn.close()
