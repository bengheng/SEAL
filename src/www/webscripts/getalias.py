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


if len(sys.argv) != 4 :
	print 'Usage: %s <fwdaddx> <aliasname> <randstr>'
	sys.exit(0)

fwdaddx = sys.argv[1]
aliasname = sys.argv[2]
randstr = sys.argv[3]

subjtmpl = 'Created new alias $aliasname.$randstr@$srvfqdn'

textversion = """

You requested for an alias. You can distribute any of the following SEAL aliases to your contacts.

(1) $aliasname.$randstr@$srvfqdn
(2) $aliasname_$randstr@$srvfqdn
(3) $aliasname-$randstr@$srvfqdn

Email sent to these aliases will be relayed to your inbox. Note that the only difference amongst them is the separator used, which could be a period '.', an underscore '_', or a dash '-'.

"""

htmlversion = """

<html>
<body>

You requested for an alias. You can distribute any of the following SEAL aliases to your contacts.<br><br>

<ol>
<li>$aliasname&#46;$randstr@$srvfqdn</li>
<li>$aliasname&#95;$randstr@$srvfqdn</li>
<li>$aliasname&#45;$randstr@$srvfqdn</li>
</ol>
<br>
Email sent to these aliases will be relayed to your inbox. Note that the only difference amongst them is the separator used, which could be a period '.', an underscore '_', or a dash '-'.

</body>
</html>

"""

srvfqdn = socket.getfqdn()

mailfrom = '\"Alias Creation Service\" <getalias@'+srvfqdn+'>'
subject = Template(subjtmpl).safe_substitute({'aliasname':aliasname,
	'randstr':randstr,
	'srvfqdn':srvfqdn})
msgtxt = Template(textversion).safe_substitute({'aliasname':aliasname,
	'randstr':randstr,
	'srvfqdn':srvfqdn})
msghtml = Template(htmlversion).safe_substitute({'aliasname':aliasname,
	'randstr':randstr,
	'srvfqdn':srvfqdn})

sendmail.sendmail_htmlmultipart(mailfrom, [fwdaddx], subject, msgtxt, msghtml)
