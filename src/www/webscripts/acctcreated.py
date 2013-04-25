#!/usr/bin/python

#import smtplib
#from email.mime.text import MIMEText
#from email.mime.multipart import MIMEMultipart
#from email.message import Message

from string import Template
#import os
#import re
import sys
#import cgi
import socket
import string
#import random
#import hashlib
import sqlite3
import sendmail
import traceback
#import subprocess

subject = 'SEAL Account Created'

textversion = """

You have successfully created your SEAL account using the username $username.
SEAL protects your personal email address by allowing you to create aliases to
be sent to your contacts.

Here's a summary of what you should do.
* Login to SEAL.
* Clicking on "Get Alias" on right.
* Enter an alias name and click "Get Alias!".
* Distribute your new SEAL alias to your friends and contacts.

Have fun!

SEAL Admin

"""

htmlversion = """

<html>
<body>

You have successfully created your SEAL account using the username
<i>$username</i>.
<br><br>
SEAL protects your personal email address by allowing you to create aliases to
be sent to your contacts.
<br><br>
Here's a summary of what you should do.
<ol>
<li>Login to SEAL.</li>
<li>Clicking on <a
href="https://seal.eecs.umich.edu/getalias.php">Get Alias</a> on right.</li>
<li>Enter an alias name and click "Get Alias!".</li>
<li>Distribute your new SEAL alias to your friends and contacts.</li>
</ol>
<br>
Have fun!
<br><br>
SEAL Admin
</body>
</html>

"""

username = sys.argv[1]

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
	mailfrom = 'noreply@'+socket.getfqdn()
	msgtxt = Template(textversion).safe_substitute({'username':username})
	msghtml = Template(htmlversion).safe_substitute({'username':username})
	sendmail.sendmail_htmlmultipart(mailfrom, [fwdaddx], subject, msgtxt, msghtml)

conn.close()
