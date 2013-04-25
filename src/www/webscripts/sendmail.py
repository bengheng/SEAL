#!/usr/bin/python

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import Message

def sendmail_htmlmultipart(mailfrom, rcpttos, subject, msgtxt, msghtml):
	mht = Message()
	mht.set_type("text/html")
	mht.set_payload(msghtml)

	msg = MIMEMultipart('alternative')
	msg.attach(MIMEText(msgtxt))
	msg.attach(mht)
	msg['From'] = mailfrom
	msg['To'] = ', '.join(rcpttos)
	msg['Subject'] = subject

	server = smtplib.SMTP('127.0.0.1', 10026)

	try:
		server.sendmail(mailfrom, rcpttos, msg.as_string())

	except smtplib.SMTPRecipientsRefused as e:
		logging.warning('Unexpected error: Recipients Refused: %s', e.recipients)

	finally:
		server.quit()

