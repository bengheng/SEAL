#!/usr/bin/python

from email.message import Message
import smtplib
import sys

import cloak.address
import cloak.alias
from cloak.db import DB
from cloak.alias import Alias
from cloak.address import Address
from cloak.config import Config
from cloak.service import Service
from cloak.user import User

if len(sys.argv) < 3:
	print "Usage Error: should be called as: {progname} <username> <alias name>".format(progname=sys.argv[0])
	sys.exit(0)

userdesc  = sys.argv[1]
alias_name = sys.argv[2]

def send_msg(mailfrom, rcpttos, msg):

	if rcpttos == []:
		return True

	server = smtplib.SMTP('127.0.0.1', 10026)

	try:
		server.sendmail(mailfrom, rcpttos, msg.as_string())

	except smtplib.SMTPRecipientsRefused as e:
		logging.warning('Recipients Refused: %s', e.recipients)

	finally:
		server.quit()

	return True

cfg = Config('/home/john/cloak/src/Scripts/alias.cfg', nolog=True)
seal_svc = Service(cfg, send_msg)

user_data = seal_svc.db.get_user(uid=userdesc)

if not user_data:
	print 'Error:BadUser'
	sys.exit(0)

user = User(**user_data)

x = Message()
x['Subject'] = alias_name

alias_addx = seal_svc.create_alias(user, None, None, x)

if alias_addx:
	print alias_addx.localpart

else:
	print 'Error:AliasCreationFailure'

