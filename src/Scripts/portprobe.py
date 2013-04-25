#!/usr/bin/env python

import socket
import smtplib

from email.mime.text import MIMEText

def send_email( frm, to, host, port ):
	msg = MIMEText( "Failed to contact \""+host+"\" on port "+str(port)+"!" )
	msg['Subject'] = 'No contact with \"'+host+"\" on port "+str(port)
	msg['From'] = frm
	msg['to'] = ','.join(to)

	s = smtplib.SMTP('cliff.eecs.umich.edu')

	print 'Sending email from '+frm+' to '+','.join(to)+'.'
	s.sendmail( frm, to, msg.as_string() )



host = "seal.eecs.umich.edu"
port = 80

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	s.connect( (host, port))
	s.shutdown( 2 )
	print "Success connecting to "
	print host + " on port: " + str(port)
except:
	print "Cannot conenct to "
	print host + " on port: " + str(port)
	send_email( 'panic@seal.eecs.umich.edu', ['bengheng@eecs.umich.edu', 'crowella@eecs.umich.edu'], host, port )
