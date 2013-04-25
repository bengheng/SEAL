#!/usr/bin/python

import sys
from string import Template
import socket
import sendmail

if len(sys.argv) != 3:
	print 'Usage: %s' % sys.argv[0]
	sys.exit(0)

uniqname = sys.argv[1]
vcode = sys.argv[2]

subject = 'SEAL Verification'

textversion = """

Please paste the link below into the URL bar of your browser to continue creating your SEAL account.

$linkola

"""

htmlversion = """

<html>
<body>
Please follow <a href="$linkola">this link</a> to continue creating your SEAL account.
</body>
</html>

"""

srvfqdn = socket.getfqdn()
mailfrom = 'noreply@'+srvfqdn
rcpttos = ['{name}@umich.edu'.format(name=uniqname)]

link = 'https://'+srvfqdn+'/adduser.php?mailverify={veri}'.format(veri=vcode)
msgtxt = Template(textversion).safe_substitute({'linkola':link})
msghtml = Template(htmlversion).safe_substitute({'linkola':link})
sendmail.sendmail_htmlmultipart(mailfrom, rcpttos, subject, msgtxt, msghtml)
