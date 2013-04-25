#!/usr/bin/python

""" Runs the content filter that processs messages through the alias service;

	Version 0.1 created: June 29, 2011
"""

import asyncore
import email
import logging
import smtpd
import smtplib
import traceback
import sys
import socket
from cStringIO import StringIO

import cloak.logdb
from cloak.user import User
from cloak.config import Config
from cloak.service import Service
from cloak.address import Address
from cloak.message import Message
from cloak.errormsg import ErrorMessage

class CloakSMTPServer(smtpd.SMTPServer):

	def __init__(self, localaddr, remoteaddr):
		self.cfg	= Config()
		self.serv	= Service(self.cfg, self.send_msg)

		logging.debug('Local Address\t\t: %s', str(localaddr))
		logging.debug('Database\t\t\t: %s',  self.cfg.DBSRC)
		logging.debug('Server FQDN\t\t: %s', self.cfg.DOMAIN)

		smtpd.SMTPServer.__init__(self, localaddr, remoteaddr)
		return

	def process_message(self, peer, mailfrom, rcpttos, data):
		logging.debug('#'*70)

		cloak.logdb.WRITE_TO_LOGDB(data, peer, mailfrom, rcpttos)

		logging.debug('Received from\t\t: %s %d', peer[0], peer[1])
		logging.info ('Envelope from\t\t: %s', mailfrom)
		logging.info ('Envelope to\t\t: %s', rcpttos)
		logging.info ('Message length\t\t: %d', len(data))
		logging.debug('Message Contents:\n%s', data)

		msg = email.message_from_string(data, _class=Message)

		# If the envelope does not have a from address,
		# use the message's from address.
		if mailfrom == '<>':
			mailfrom = msg['From']

		fromaddx = Address(mailfrom)
		username = fromaddx.parse_user_address()
		logging.debug('From User\t\t: %s (%s)', username, mailfrom);

		# Gmail sends a verification email when the user creates a "Send
		# As" account. We trap that mail based on SUPPORTEDMAIL and
		# resends it back to the Gmail account so that the user can
		# click on the verification link.
		SUPPORTEDMAIL = ['mail-noreply@google.com']
		fwdverify = msg.get_header_addresses('From')

		if len(rcpttos) == 1 and			 \
		   len(fwdverify) == 1 and			 \
		   fwdverify[0].address in SUPPORTEDMAIL:
			rcptto = Address(rcpttos[0])
			if rcptto.parse_user_address():
				return self.serv.sender_verify_forward(mailfrom, rcpttos, msg)

		if username:
			# Case 1:
			userdata = self.serv.db.get_user(username=username)
			if not userdata:
				logging.warning('User was validated to send mail, ' \
						'but has no data in user table!')
				return

			user = User(**userdata)

			logging.debug('UID\t\t\t: %s', user.get_uid())
			logging.debug('Forwarding Address\t: %s', user.get_forwarding_address())
			logging.debug('Salt\t\t\t: %s', user.get_salt())

			# TODO: Case 1a:

			if len(rcpttos) == 1 and msg.get_header_length('To') == 1:
				# Case 1b: Message sent to getalias with new
				# alias in "Subject" field.
				rcptto = Address(rcpttos[0])

				if rcptto.is_getalias():
					logging.debug('===== CASE 1B OR LS REQUEST =====')
					self.serv.dispatch_getalias(user, mailfrom, rcpttos, msg)
					return

				elif rcptto.is_svcalias():
					logging.debug('===== PERMISSION RESPONSE RECEIVED =====')
					self.serv.allow_sender(user, mailfrom, rcpttos, msg)
					return
					
				elif rcptto.is_untrusted():
					logging.debug('===== UNTRUSTED TRANSITION REQUEST =====')
					self.serv.apply_untrusted(user, mailfrom, rcpttos, msg)
					return

				elif rcptto.is_removealias():
					return # TODO: support remove alias?

			# Test for case 1c: Message not addressed to getalias@service.com but
			# contains exactly one properly formatted alias request address in the
			# "To" field.
			is_areq_address = lambda entry: entry.parse_areq_address()

			# Checks that there is only one alias request address in
			# the "To" field.
			areq_rcpt = None
			for cur_rcpt in msg.search_header_addresses('To', is_areq_address):
				if areq_rcpt is not None:
					# bad input (we found more than one alias request address)
					logging.debug('Found more than 1 alias request address!')

					err = ErrorMessage('filtermain.toomanyareq',
							   fromaddx	= self.cfg.GETALIAS,
							   toaddx	= user.get_account_address(),
							   subject	= msg['Subject'])

					self.serv.send_msg(err['From'], [user.get_forwarding_address()], err)
					return

				areq_rcpt = cur_rcpt

			if areq_rcpt:
				# Case 1c:
				logging.debug('===== CASE 1C =====')
				return self.serv.create_send_alias(user, areq_rcpt, mailfrom, rcpttos, msg)
			
			# Cases 1d-e:
			logging.debug('===== CASE 1D/E =====')
			return self.serv.apply_aliasing(user, mailfrom, rcpttos, msg)

		else:	# Case 2:
			if len(rcpttos) == 1:
				rcptto = Address(rcpttos[0])
				if rcptto.is_captcha():
					logging.debug('==== CAPTCHA ====')
					self.serv.recv_captcha(mailfrom, msg)
					return

			logging.debug('===== CASE 2 =====')
			self.serv.forward(mailfrom, rcpttos, msg)

		return

	def send_msg(self, mailfrom, rcpttos, msg):

		if rcpttos == []:
			logging.info('send_msg called with empty rcpttos; skipping.')
			return True

		outstr = StringIO()
		server = smtplib.SMTP('127.0.0.1', 10026, output=outstr)

		# Show communication with the server;
		if self.cfg.LOGLEVEL <= logging.INFO:
			server.set_debuglevel(True)

		try:
			logging.info('Sending mail...')

			# Save original stdout and assign to string
			server.sendmail(mailfrom, rcpttos, msg.as_string())

			logging.info('=== Server Output ===\n%s', outstr.getvalue())

			self.tell_test_server(outstr.getvalue())

			cloak.logdb.WRITE_TO_LOGDB(outstr.getvalue())

		except smtplib.SMTPRecipientsRefused as e:
			logging.warning('Recipients Refused: %s', e.recipients)

		finally:
			server.quit()

		return True

	def tell_test_server(self, msg):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect(('127.0.0.1', 45678))
			s.send(msg)
			s.close()
		except:
			logging.debug('Cannot connect to test server. Nothing is harmed.')


server = CloakSMTPServer(('127.0.0.1', 10025), None)
asyncore.loop()
