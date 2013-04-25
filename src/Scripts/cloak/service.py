
""" Class providing the alias service.

	Version 0.1 created: July 5, 2011
"""

#from recaptcha.client import captcha

import os
import sys
import time
import string
import logging

import user
import alias
import usermsg
import captcha
import address
import errormsg
from db import DB
from user import User
from alias import Alias
from config import Config
from message import Message
from address import Address
from usermsg import UserMessage
from errormsg import ErrorMessage

def default_send_fn(self, mailfrom, rcpttos, msg):
	logging.debug('mailfrom: %s', mailfrom)
	logging.debug('rcpttos: %s',  rcpttos)
	logging.debug('Message: %s',  msg.as_string())
	return

class Service(object):

	cfg	= None
	db	= None
	send	= None

	def __init__(self, cfg, send_fn=default_send_fn):
		try:
			self.cfg	= cfg
			self.send	= send_fn

			address.cfgdata	  = self.cfg
			alias.cfgdata	  = self.cfg
			errormsg.cfgdata  = self.cfg
			user.cfgdata	  = self.cfg
			usermsg.cfgdata   = self.cfg

			self.db  = DB(self.cfg)
		except:
			logging.warning('Alias service could not be started')
			raise


	def apply_aliasing(self, user, mailfrom, rcpttos, msg):
		""" Applies an alias as the sender of a message or attempts to infer
		it if none was given by the sender.

		Handles cases 1d and 1e of the specification.
		"""
		usralias = None
		alias_addx = None
		is_alias_address = lambda entry: entry.parse_alias_address()

		logging.debug('Attempting to apply aliasing')

		# look for use of existing alias in To field (case 1d);
		for cur_addx in msg.search_header_addresses('to', is_alias_address):
			alias_pair = cur_addx.parse_alias_address()
			alias_data = self.db.get_alias_data(*alias_pair,	\
							    uid=user.get_uid())

			if not alias_data:
				continue

			usralias = Alias(**alias_data)
			alias_addx = cur_addx

			#if not usralias.is_active():
			#	continue

			# remove alias from rcpttos and all To fields
			for i in range(len(rcpttos)):
				if alias_addx == rcpttos[i]:
					del rcpttos[i]
					break

			msg.replace_address('to', alias_addx, None)
			break

		# if no alias in To field, try to infer the correct one (case 1e);
		if not alias_addx:

			logging.debug("Couldn't find alias to use in headers; " \
				      'attempting to infer correct alias')

			alias_data = self.db.infer_alias(user.get_uid(),
							 msg.get_header_addresses('to'),
							 user.get_salt())

			if not alias_data:
				logging.debug('Failed to infer alias')

				err = ErrorMessage('applyalias.noinfer',
						   fromaddx = self.cfg.SVCALIAS,
						   toaddx = user.get_account_address(),
						   subject = msg['Subject'])
	
				self.send(err['From'], [user.get_forwarding_address()], err)

				return False

			usralias = Alias(**alias_data)

			#if not usralias.is_active():
			#	return False

			logging.debug('Succesfully inferred alias "%s"', str(usralias))

			alias_addx = Address(usralias.get_alias_address())

		# if we found an alias to use, apply it, send the
		# message, and record in history table;
		alias_addx.realname = Address(mailfrom).realname

		msg.replace_address('from', None, alias_addx)
		#del msg['message-id']

		if rcpttos == []:
			logging.info('No recipients left; ignoring');
			return

		rcpt_aliases = []
		rcpt_nonaliases = []

		for entry in rcpttos:
			rcpt_addx = Address(entry)
			if rcpt_addx.is_servername():
				rcpt_aliases.append(entry)
			else:
				rcpt_nonaliases.append(entry)

		self.send(str(alias_addx), rcpt_nonaliases, msg)
		self.forward(str(alias_addx), rcpt_aliases, msg)

		self.db.add_history(usralias.get_rid(),
				    True,
				    address.getaddresses(rcpttos),
				    msg['Message-ID'],
				    user.get_salt())

		return

	def dispatch_getalias(self, user, mailfrom, rcpttos, msg):
		''' Dispatches commands sent to getalias@<service>.
		'''

		command = msg['Subject'].split(' ')

		if command[0].lower() == 'ls':
			if len(command) == 1:
				self.list_aliases(user, mailfrom, rcpttos, msg)
			else:
				logging.debug('Command error.')
		else:
			self.create_alias(user, mailfrom, rcpttos, msg)

		return
		

	def create_alias_helper(self, user, aliasname, \
	primary=False, rcpt=None, trusted=True, hint=None):
		""" Helper function to create alias.
		Generates <rand> for user for the <aliasname> specified.
		If <aliasname> belonging to the user already exists, the existing aid is used.
		If <aliasname> belonging to another user already exists, an error is returned.
		"""
		(aid, uid) = self.db.get_aliasname_data(aliasname)

		# Error if user doesn't own the aliasname
		if uid != None and uid != user.get_uid():
			logging.info('User %d does not own "%s".', user.get_uid(), aliasname)

			# Create error response message
			err = ErrorMessage('createalias.notowner',
					   fromaddx	 = self.cfg.GETALIAS,
				           toaddx	 = user.get_account_address(),
					   aliasname	 = aliasname)

			self.send(err['From'], [user.get_forwarding_address()], err)
			return None

		#
		# Now, aliasname either belongs to the user or is not in use.
		#

		# Gets the alias id, either by getting an existing one or create a new one.
		if uid == user.get_uid():
			newaid = aid
			logging.debug('Using existing aid %d for aliasname "%s"',	\
					newaid, aliasname)
		elif uid == None:
			newaid = self.db.insert_alias(user.get_uid(), aliasname, primary)
			logging.debug('Created new aid %d for aliasname "%s"',	\
					newaid, aliasname)
		else:
			return None

		#
		# If a recipient is given, check history to see if there was any
		# previously generated <rand> that we can use.
		# TODO: We might have to make sure the recipient is active.
		#

		newalias = None
		cid = None
		if rcpt != None:
			cid = self.db.peek_cid(rcpt, user.get_salt())

		rid = None
		if cid != None:
			rid = self.db.get_history_rid(aliasname, cid)
			if rid != None:
				# Found a history correspondence
				hist_alias = Alias(self.db.get_alias_data(rid))
				hist_aliasname, hist_aliasrand = hist_alias.get_alias_pair()

				logging.debug('History aliasname\t:"%s"', hist_aliasname)

				if hist_aliasname == aliasname:
					logging.debug('Reuse history aliasrand\t:"%s"', \
							hist_aliasrand)
					newalias = Alias(hist_aliasname, hist_aliasrand)
				else:
					# Can't use the rid found since aliasname differs
					rid = None


		# Create a new alias (aka aliasrand or <aliasname>.<rand>)
		if newalias == None:
			logging.debug('Generating new aliasrand')
			newalias = Alias(aliasname, alias.generate_rint())

		logging.debug('Using alias\t\t: %s', newalias)

		# Update aid, uid and set isactive for new alias
		newalias.set_values(aid=newaid, uid=user.get_uid(), isactive=1)

		# Sets up alias pair
		alias_pair = newalias.get_alias_pair()

		# If we don't have rid yet, insert aliasrand to DB and mark as active
		if rid == None:
			rid = self.db.insert_aliasrnd(user.get_uid(),	\
				newaid,					\
				alias_pair[0], alias_pair[1],		\
				1, trusted, hint)
		if rid == None:
			return None

		# Looks like this double counts in the history table;
		#if rcpt != None:
		#	self.db.add_history(rid, True, [rcpt], user.get_salt())


		# Creates the alias address, which includes the domain
		aliasaddx = Address(newalias.get_alias_address())
		logging.info('Aliasrnd Address\t\t: %s', str(aliasaddx))
		return aliasaddx

	def create_alias(self, user, mailfrom, rcpttos, msg):
		"""  Handles Case 1b, for creating a new alias.
		"""
		# Use first string token as aliasname.
		# The second string token can specify options.
		# Current options supported:
		# - UNTRUSTED
		# - HINT <hint>
		aliastokens = msg['Subject'].rsplit(' ')
		aliasname = aliastokens[0]
		isprimary = False
		istrusted = True
		hint = None
		# TODO: This is not the most robust way to parse options,
		# but will do for now.
		if len(aliastokens) > 1:
			for t in range(1, len(aliastokens)):
				opt = aliastokens[t].lower()
				if opt == 'untrusted':
					istrusted = False
				elif opt == 'primary':
					isprimary = True
				elif opt == 'hint' and t < (len(aliastokens)-1):
					hint = aliastokens[t+1]

		

		# aliasname must be properly formatted
		if not alias.is_alias_name(aliasname):
			logging.info('Improper aliasname format: "%s"', aliasname)

			# Create error response message
			err = ErrorMessage('createalias.badalias',
					   fromaddx	 = self.cfg.GETALIAS,
				           toaddx	 = user.get_account_address(),
					   aliasname	 = aliasname,
					   maxlen	 = self.cfg.MAXALIASNAMELEN)

			self.send(err['From'], [user.get_forwarding_address()], err)
			return

		aliasaddx = self.create_alias_helper(user, aliasname, rcpt=None, \
			primary=isprimary, trusted=istrusted, hint=hint)

		if aliasaddx == None:
			# Something went terribly wrong
			return

		# Create response message
		msg = UserMessage('createalias.aliascreated',
				  fromaddx	= self.cfg.GETALIAS,
				  toaddx	= user.get_account_address(),
				  aliasaddx	= aliasaddx)

		self.send(msg['From'], [user.get_forwarding_address()], msg)

		return

	def create_send_alias(self, user, areq, mailfrom, rcpttos, msg):
		""" Handles Case 1c, for creating a new alias and sending the message under it.
		"""
		aliasname = areq.parse_areq_address()

		# If there are exactly two recipients, the other recipient could
		# be used as a hint to create_alias_helper to search the
		# history for reusable random string. If there are more than two
		# recipients, create_alias_helper will just create a new random
		# string.
		msgtos = msg.get_header_addresses('to')
		other_rcpt = None
		if len(msgtos) == 2:
			for t in msgtos:
				if str(t) != str(areq):
					other_rcpt = t
					break

		aliasaddx = self.create_alias_helper(user, aliasname, other_rcpt)
		if aliasaddx == None:
			# Something went terribly wrong
			return

		# Replace request address in message and envelope
		msg.replace_address('to', areq, aliasaddx)		

		forareq = False
		for r in range(len(rcpttos)):
			if areq == rcpttos[r]:
				forareq = True
				rcpttos[r] = str(aliasaddx)
				break

		# Create a string that excludes areq
		strmsgtos = ''
		for r in range(len(msgtos)):
			if not( areq == msgtos[r] ):
				strmsgtos = strmsgtos + str(msgtos[r]) + '\r\n'

		if forareq == True:
			# Tell the user which aliasname is used.
			umsg = UserMessage('createsendalias.aliascreated',
					   fromaddx	= self.cfg.GETALIAS,
					   toaddx	= user.get_account_address(),
					   aliasaddx	= aliasaddx,
					   subject	= msg['Subject'],
					   rcpts	= strmsgtos)

			self.send(umsg['From'], [user.get_forwarding_address()], umsg)

			# If the mail is strictly intended for the alias request
			# address, we don't need to process it further.
			if len(rcpttos) == 1:
				return

		logging.debug('PASSTHROUGH')
		self.apply_aliasing(user, mailfrom, rcpttos, msg)
		return

	def list_aliases(self, user, mailfrom, rcpttos, msg):
		"""  Returns list of previously used aliases to sender.
		"""
		alist = self.db.get_aliases(user.get_uid())
		aliststr = '\n'.join(map(lambda x: Alias(*x).get_alias_pair(), alist))

		# Create response message
		umsg = UserMessage('listalias.get',
				   fromaddx	= self.cfg.GETALIAS,
				   toaddx	= user.get_account_address(),
				   subject	= msg['Subject'],
				   aliaslist	= aliststr)

		self.send(msg['From'], [user.get_forwarding_address()], umsg)

		return

	def sender_verify_forward(self, mailfrom, rcpttos, msg):
		""" Forwards mail to user of our service.
		The criteria for forwarding to user is that there is only 1
		recipient and the sender is a noreply for a supported email service;
		"""

		if len(rcpttos) != 1:
			return

		# Must be using our servername
		prcpt = Address(rcpttos[0])
		username = prcpt.parse_user_address()

		if not username:
			return

		# Must be a user of our service
		userdata = self.db.get_user(username=username)

		if userdata == False:
			return
		
		# Now we can forward 
		user = User(**userdata)

		logging.debug('Forwarding verification mail to service user at %s', \
			      user.get_forwarding_address())

		self.send(mailfrom, [user.get_forwarding_address()], msg)

		return

	def forward(self, mailfrom, rcpttos, msg):
		""" Handles Case 2, where email is not from a service user and so
		needs to be forwarded to various aliases.
		"""
		for rcpt in rcpttos:
			prcpt = Address(rcpt)
			alias_pair = prcpt.parse_alias_address()
			logging.debug(rcpt)
			if not alias_pair:
				# if the domain is SERVERNAME, sender screwed up; return error to sender...
				if prcpt.is_servername():
					logging.info('Encountered improperly formatted '
						     'address "%s" in recipients field', prcpt.address)

					# Create error response message
					err = ErrorMessage('forward.badformat',
							   fromaddx	= self.cfg.SVCALIAS,
							   toaddx	= mailfrom,
							   badalias	= prcpt.address)

					self.send(err['From'], [mailfrom], err)

				# ... otherwise ignore; not our job to send to non-users
				logging.info('Encountered recipient outside our domain; ignoring')

			else:
				alias_data = self.db.get_alias_data(*alias_pair)

				if alias_data:
					fwd_alias = Alias(**alias_data)

					userdata = self.db.get_user(uid=fwd_alias.get_uid())
					assert userdata is not None
					user = User(**userdata)

					logging.debug('is trusted? %s', fwd_alias.is_trusted())

					# handle trustedness here;
					if not fwd_alias.is_trusted():

						mfrom = Address(mailfrom)

						# if sender is in trusted group, then it's all right;
						if self.db.is_trusted_correspondent(mfrom,			\
										    user.get_salt(),		\
										    fwd_alias.get_rid(),	\
										    fwd_alias.get_trusted_timestamp()):
							pass # TODO: send/append something about newer alias to send to?

						else:
							capstat = self.db.get_capstat(mfrom,		\
										      user.get_salt(),	\
										      fwd_alias.get_rid())

							logging.debug('capstat=%s', capstat)

							if capstat < self.db.CAPTCHA_PENDING:
								logging.debug('captcha not yet sent; trying to send one')
								# If not approved, send captcha to sender and drop mail.
								# TODO: Perhaps we can cache the mail somewhere.
								cid = self.db.get_cid(mfrom, user.get_salt())
								self.send_captcha(mailfrom, cid, fwd_alias)
								#self.db.set_capstat(cid,
								#		    fwd_alias.get_rid(),
								#		    self.db.CAPTCHA_PENDING)
								logging.debug('done sending captcha')

							elif capstat == self.db.CAPTCHA_PENDING:
								logging.debug('captcha was already sent; still waiting for solution')

							elif capstat == self.db.CAPTCHA_APPROVED:
								logging.debug('captcha approved, but not yet user approved')
								# if user denied,
								# TODO: just ignore? or do something more?
								#	pass

								# if user judgement pending, send message
								# informing them they must wait for user's approval?
								if capstat == self.db.USER_PENDING:
									pass # TODO: send message

							return

					# TODO: can consult a whitelist/blacklist/etc. here

					fwd_addx = Address(user.get_forwarding_address())
					fwd_addx.realname = prcpt.realname

					logging.info('Found alias for account (%s) Forwarding message to %s', \
						      user.get_username(), fwd_addx.address)

					# Add hint as recipient name. The hint/domain is used as a reminder
					# to the user where this email address was originally created for.
					# But since we did not update Reply-To, it will drop off when the
					# user replies to the message.
					rcptaddr = Address(rcpt)

					if rcptaddr.get_realname() == '':
						if fwd_alias.get_hint() != None:
							rcptaddr.set_realname(fwd_alias.get_hint())

						elif fwd_alias.get_domain() != None:
							rcptaddr.set_realname(fwd_alias.get_domain())

						msg.replace_address('To', rcpt, rcptaddr)

					acct_addx = Address(user.get_account_address())
					acct_addx.realname = prcpt.realname

					#del msg['message-id']
					#del msg['DKIM-Signature']

					if 'To' in msg:
						msg.replace_header('To', msg['To'] + ', ' + str(acct_addx))

					if 'Reply-To' in msg:
						msg.replace_header('Reply-To', msg['reply-to'] + ', ' + rcpt);
					else:
						msg.add_header('Reply-To', mailfrom + ', ' + rcpt);

					if 'Message-ID' not in msg:
						msg.generate_message_id(self.cfg.DOMAIN)

					self.send(mailfrom, [str(fwd_addx)], msg)
					self.db.add_history(fwd_alias.get_rid(), False, [Address(mailfrom)], msg['Message-ID'], user.get_salt())

				else:
					logging.info("Couldn't find data for alias (%s,%d)", *alias_pair)

		return

	def apply_untrusted(self, user, mailfrom, rcpttos, msg):

		if 'In-Reply-To' in msg:
			hashmsg = self.db.hash_data(msg['In-Reply-To'], user.get_salt())
		else:
			return # TODO: error; message-id should always be present

		self.db.set_untrusted_alias(user.get_uid(), hashmsg)
		return

	def allow_sender(self, user, mailfrom, rcpttos, msg):

		self.db.allow_sender(user.get_uid(), msg['In-Reply-To'])

	def send_captcha(self, mailfrom, cid, fwd_alias, orgidentifier=None):
		""" Sends mail attached with captcha image.
		"""

		# Generate captcha image
		logging.debug('Sending captcha')

		word = captcha.gen_random_word()
		identifier = self.db.hash_data(Address(mailfrom).address, word)
		captchafile = identifier+'.jpg'
		captcha.gen_captcha(word.strip(), 'porkys.ttf', 25, captchafile)

		msg = UserMessage('senderverify.sendcaptcha',	\
				images		= [captchafile],	\
				identifier	= identifier,		\
				fromaddx	= self.cfg.CAPTCHA,	\
				toaddx		= mailfrom)

		logging.debug('Sending captcha to %s', mailfrom)
		self.send(msg['From'], [mailfrom], msg)
		os.remove(captchafile)

		# Replace identifier and word
		if orgidentifier != None:
			logging.debug('Replacing CAPTCHA id %s', orgidentifier)
			self.db.replace_captcha_identifier(orgidentifier, identifier, word)

		# Insert identifier into db
		logging.debug('CAPTCHA id %s, word %s, cid %d', identifier, word, cid)
		self.db.set_captcha(identifier, word, cid, fwd_alias.get_rid(), self.db.CAPTCHA_PENDING)

	def recv_captcha(self, mailfrom, msg):
		""" Receives and verifies captcha.
		"""
		subject = msg['Subject']
		orgidentifier = string.split(subject,' ')[-1]
		logging.debug('Orig CAPTCHA identifier\t: %s', orgidentifier)

		# TODO: Reject if original identifier is not in DB

		try:
			if msg.is_multipart():
				answer = msg.get_payload(0).get_payload().splitlines()[0].strip()
			else:
				answer = msg.get_payload().splitlines()[0].strip()
		except:
			return

		identifier = self.db.hash_data(Address(mailfrom).address, answer)
		match = self.db.get_captcha_word(identifier)
		if match != None and match['word'] == answer:
			# Update captcha status to CAPTCHA_APPROVED
			cid, rid, word = match

			adata = self.db.get_alias_data(rid)
			aobj  = Alias(**adata)
			user  = User(**self.db.get_user(uid=aobj.get_uid()))

			# send message to recipient's alias requesting mailfrom's permission to send
			msg = UserMessage('senderverify.senduserreq',			\
					  fromaddx	= self.cfg.SVCALIAS,		\
					  aliasaddx	= aobj.get_alias_address(),	\
					  useraddx	= user.get_account_address(),	\
					  requestor	= mailfrom)

			msg.generate_message_id(self.cfg.DOMAIN)

			self.db.set_captcha(msg['Message-ID'], '', cid, rid, self.db.CAPTCHA_APPROVED)

			logging.debug('Sending approval request to user %s', user.get_username())
			self.send(msg['From'], [user.get_forwarding_address()], msg)

			# Delete identifier from database
			#self.db.delete_captcha_identifier(identifier)

		else:
			# TOFIX: should replace with new captcha and increment numtries;
			pass
			# Resend captcha
			#self.send_captcha(mailfrom, orgidentifier=orgidentifier)

