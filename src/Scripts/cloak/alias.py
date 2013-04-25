
""" Class for managing alias information;

	Version 0.1 created: July 5, 2011
"""

import random
import string
import logging

import config

cfgdata = None

class Alias(object):

	aliasfields	= ['rid',
			   'aid',
			   'uid',
			   'aliasname',
			   'aliasrand',
			   'isactive',
			   'istrusted',
			   'truststamp',
			   'hint',
			   'domain'
			  ]

	def __init__(self, *aliasargs, **aliasdata):
		""" Initializes an Alias object.

		Can be called either with just keywords (i.e. from an sqlite row
		entry taken from the database) or by taking an alias name and
		randomization string (in integer form) as well as optional
		additional keywords.
		"""
		self.set_values(_init=True, **aliasdata)

		# object can be initialized with just an alias pair (see below)
		naliasargs = len(aliasargs)
		if naliasargs == 2:
			self.aliasname = aliasargs[0]
			self.aliasrand = aliasargs[1]
	
			logging.debug('Using aliasname\t\t: "%s"', self.aliasname);
			logging.debug('Using rand\t\t: %s', self.aliasrand)

		elif naliasargs != 0:
			raise TypeError('__init__() takes exactly 0 or 2 ' \
			'non-keyword arguments ({n} given)'.format(n=naliasargs))

	def set_values(self, _init=False, **newdata):
		""" Sets values, normally passed in by a row from the database.
		"""
		for key in self.aliasfields:

			if key in newdata.keys():
				self.__dict__[key] = newdata[key]
			elif _init:
				self.__dict__[key] = None

		return

	def __str__(self):
		""" Returns the string representation of the alias, which is the same
		as the local part of the full alias address, using the default separator.
		NOTE: Do not compare alias addresses on this string form; the separator
		could be different.
		"""
		return '{aname}{sep}{rstr}'.format(aname = self.aliasname,		\
						   sep   = cfgdata.DEFAULTSEPARATOR,	\
						   rstr  = rint_to_rstr(self.aliasrand))

	def get_rid(self):
		""" Returns the rid of the alias.
		"""
		return self.rid

	def get_aid(self):
		""" Returns the aid of the alias.
		"""
		return self.aid

	def get_uid(self):
		""" Returns the uid of the owner of this alias.
		"""
		return self.uid

	def get_hint(self):
		""" Returns the hint corresponding to this alias.
		"""
		return self.hint

	def get_domain(self):
		""" Returns the domain corresponding to this alias.
		"""
		return self.domain

	def get_aliasname(self):
		""" Returns the alias name of this alias.
		"""
		return self.aliasname

	def get_aliasrand(self):
		""" Returns the integer representation of the randomization string.
		"""
		return self.aliasrand

	def get_alias_pair(self):
		""" Returns an alias pair.

		An alias pair is a tuple whose first entry is the
		alias name and whose second entry is the integer representation of
		the randomization string.  Used internally to represent an alias before
		an Alias object has been created and in interaction with the database.
		"""
		return (self.aliasname, self.aliasrand)

	def get_alias_address(self):
		""" Given an alias pair of the form (aname, rstr) where aname is the alias
		name and rint is the integer representation of the random string, returns
		the properly formatted alias address that corresponds to that pair.
		"""
		#if self.hint != None:
		#	logging.debug('Using hint\t\t: %s', self.hint)
		#	return '{hint} <{localpart}@{domain}>'.format(	\
		#		hint		= self.hint,		\
		#		localpart	= self.__str__(),	\
		#		domain		= cfgdata.DOMAIN)
		
		return '{localpart}@{domain}'.format(localpart	= self.__str__(),	\
						     domain	= cfgdata.DOMAIN)

	def is_active(self):
		""" Returns whether the alias is listed as active.
		"""
		return (self.isactive != 0)

	def is_trusted(self):
		""" Returns whether the alias is marked as trusted.
		"""
		return (self.istrusted != 0)

	def get_trusted_timestamp(self):
		""" Returns the trusted timestamp for this alias, or None
		if the alias is entirely trusted.
		"""
		return None if self.is_trusted() else self.truststamp

def is_alias_name(name):
	""" Performs simple check of whether this is a properly formatted aliasname,
	verifying and returning True when it has:
		- valid format, and
		- valid length.
	"""
	if not isinstance(name,str):
		return False

	if len(name) < 1 or len(name) > cfgdata.MAXALIASNAMELEN:
		logging.debug('"%s" too long (len=%d) to be alias name; max is %d characters.', \
			      name, len(name), cfgdata.MAXALIASNAMELEN)
		return False

	# alias name must be alphanumeric string;
	for c in name:
		if not (c in string.letters or c in string.digits):
			logging.debug('"%s" does not fit format for alias name', name)
			return False

	return True

def rstr_to_rint(rstr):
	""" Converts from the "base 32" randomization string format to integer form.
	"""
	rint = 0
	exponent = 1

	if not(isinstance(rstr,str)) or len(rstr) != cfgdata.RANDLEN:
		return False

	rstr = rstr.lower()

	for i in range(cfgdata.RANDLEN):
		try:
			rchar = cfgdata.RANDALPHABET.index(rstr[-1-i])
		except ValueError:
			return False
		rint = rint + exponent*rchar
		exponent = exponent * len(cfgdata.RANDALPHABET)

	return rint

def rint_to_rstr(rint):
	""" Converts from integer form to the "base 32" string format.
	"""
	rstr = ''
	div = len(cfgdata.RANDALPHABET)

	# make sure it's in a valid range
	if not(isinstance(rint,int) or isinstance(rint,long)) or \
	   0 > rint or rint >= cfgdata.RANDSPACE:
		return False

	for i in range(cfgdata.RANDLEN):
		rstr += cfgdata.RANDALPHABET[rint % div]
		rint -= rint % div
		rint /= div

	return ''.join(reversed(rstr))

def generate_rint():
	""" Creates a new integer for a random string.
	"""
	return random.randint(0,cfgdata.RANDSPACE-1)

def generate_rstr():
	""" Creates a new random string.
	"""
	return rint_to_rstr(generate_rint())

