
""" Utilities and Address class for managing addresses and aliases.

	Version 0.1 created: July 5, 2011
"""

import email.utils
import string
import logging

import alias
import config
import user

cfgdata = None

class Address(object):

	realname	= ''
	address		= None
	localpart	= None
	domain		= None

	def __init__(self, addx):
		""" Configuration data is needed for various things including reserved
		alias names, the domain name of our service, etc.; Before using this
		class, set cfgdata to the properly initialized Config object.
		"""
		if isinstance(addx, tuple):
			self.set_address(addx[1])
			self.realname = addx[0]
	
		else:
			self.set_address(addx)

	def set_address(self, addx):
		""" Sets this address object to the new address in string addx; addx
		should be an RFC822-compliant string (e.g "Realname <addx@example.com>").
		If no real name is given, realname is left unchanged.
		"""
		addxpair = email.utils.parseaddr(addx)

		if addxpair == ('',''):
			self.address = addx
			return

		if addxpair[0] != '':
			self.realname= addxpair[0]

		# Policy is case insensitive; all service addresses treated as lowercase
		# TODO: make this happen only for service addresses;
		self.address = addxpair[1].lower()

		paddx = self._parse_email_address(self.address)

		if paddx:
			self.localpart, self.domain = paddx

		return

	def _parse_email_address(self, addx):
		""" Used internally to parse the input email address into localpart and
		domain parts upon object creation;
		"""
		if not (isinstance(addx,str) and '@' in addx):
			return False

		if len(addx) > cfgdata.MAXADDRLEN:
			return False

		paddx = addx.split('@')

		if len(paddx) != 2 or len(paddx[0]) <= 0 or len(paddx[1]) <= 0:
			return False

		else:
			return paddx

	def parse_user_address(self):
		""" Parses a user address, returning the contained username;
		Returns False if not properly formatted.
		"""
		if not isinstance(self.localpart, str) or	\
		   not (self.is_servername() and user.is_user_name(self.localpart)):
			return False

		return self.localpart

	def parse_areq_address(self):
		""" Parses an alias request address, returning the requested alias name;
		Returns False if not properly formatted.
		"""
		if not isinstance(self.localpart, str) or	\
		   not (self.is_servername() and alias.is_alias_name(self.localpart)):
			return False

		return self.localpart 

	def parse_alias_address(self):
		""" Parses an alias address from string format, returning a tuple containing
		the address' alias name and randomization string (as an integer).
		Returns False if not properly formatted.
		"""
		if not isinstance(self.localpart, str) or len(self.localpart) <= cfgdata.RANDLEN:
			return False

		# Separator is required
		if self.localpart[-cfgdata.RANDLEN-1] not in cfgdata.SEPARATORS:
			return False

		# Uncomment the following if allowing separators to be optional;
		# aliasname = self.localpart[0: -cfgdata.RANDLEN \
		#			 if self.localpart[-cfgdata.RANDLEN-1] \
		#			  not in cfgdata.SEPARATORS \
		#			 else -cfgdata.RANDLEN-1]
		aliasname = self.localpart[0: -cfgdata.RANDLEN-1]
		randstr   = self.localpart[-cfgdata.RANDLEN:]

		if not self.is_servername():
			return False

		randint = alias.rstr_to_rint(randstr)

		if randint is False or not alias.is_alias_name(aliasname):
			return False

		return (aliasname, randint)

	def get_header_address(self):
		""" Returns the RFC822 compliant header field address string for
		this address (the format is "Realname <Address>").
		"""
		if self.realname is None:
			rname = ''
		else:
			rname = self.realname

		return email.utils.formataddr( (rname, self.address) )

	def __eq__(self, addx):
		""" Allows comparing string addresses to Address objects;
		Note that to use this, the Address object must be to the
		left of the equal sign (e.g. <AliasAddx> == "bob@example.com").
		"""
		if not isinstance(addx,Address):
			addx = Address(addx)

		return (addx.address != '' and addx.address == self.address)

	def __str__(self):
		""" When used a string, outputs the result of get_header_address.
		"""
		return self.get_header_address()

	def set_realname(self, rname):
		''' Sets realname.
		'''
		self.realname = rname

	def get_realname(self):
		''' Returns realname.
		'''
		return self.realname

	def is_getalias(self):
		""" Checks whether the address is the getalias address.
		"""
		return (self.address == cfgdata.GETALIAS)

	def is_removealias(self):
		""" Checks whether the address is the remove alias address.
		"""
		return (self.address == cfgdata.REMALIAS)

	def is_captcha(self):
		""" Checks whether the address is the captcha address.
		"""
		return (self.address == cfgdata.CAPTCHA)

	def is_svcalias(self):
		""" Checks whether the address is the service alias address.
		"""
		return (self.address == cfgdata.SVCALIAS)

	def is_untrusted(self):
		""" Checks whether the address is the 'untrusted' address used
		for transitioning an alias address to the untrusted state.
		"""
		return (self.address == cfgdata.UNTRUSTED)

	def is_servername(self):
		""" Checks whether the address' domain is the server address.
		"""
		return (isinstance(self.domain, str) and self.domain == cfgdata.DOMAIN)

def getaddresses(fieldvalues):
	""" Parses a string list of RFC822 addresses, returning a list of
	Address objects representing the same string list.
	"""
	addx_list = email.utils.getaddresses(fieldvalues)

	for i in range(len(addx_list)):
		addx_list[i] = Address(addx_list[i])

	return addx_list
