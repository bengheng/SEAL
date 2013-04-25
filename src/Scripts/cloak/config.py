
""" Class used to fetch configuration data for use by Service class.

	Version 0.1 created: July 5, 2011
"""

import ConfigParser
import hashlib
import logging
import math
import string
import socket
import os
from string import Template

# Configurations are read from this file; The file must be in the same
# directory as the script that is run to use this class.
DEFAULTFILE = 'alias.cfg'
DEFAULT_PRODUCTION_SERVER_FQDN = 'cloak.dyndns-mail.com'

# Headers for different classes of configuration data;
ALIASHDR	= 'Alias Service'
USERMSGHDR	= 'User Messages'
DBHDR		= 'Database'
LOGGINGHDR	= 'Logging'
RESADDRHDR	= 'Reserved Addresses'
RANDSTRHDR	= 'Randomization Strings'

class Config(object):

	def __init__(self, cfgsrc=DEFAULTFILE):
		""" Fetches configuration data from the file named by DEFAULTFILE.
		"""
		config = ConfigParser.ConfigParser()
		config.read(cfgsrc)

		# Set up cfgvars;

		cfgvars = dict()

		if os.getenv('HOME'):
			cfgvars['HOME'] = os.getenv('HOME')
		else:
			cfgvars['HOME'] = '/home/john'

		if socket.gethostbyname(socket.gethostname()) ==	\
		   socket.gethostbyname(DEFAULT_PRODUCTION_SERVER_FQDN):
			# We need to do this because we're using
			# dyndns and python doesn't return you the
			# fqdn.
			cfgvars['FQDN'] = DEFAULT_PRODUCTION_SERVER_FQDN
		else:
			cfgvars['FQDN'] = socket.getfqdn()

		# Process configuration for Logging mechanisms;

		try:
			self.LOGFORMAT = config.get(LOGGINGHDR, 'format', 1)
		except:
			self.LOGFORMAT = '%(asctime)s %(levelname)s: %(message)s'

		try:
			strlvl = string.upper(config.get(LOGGINGHDR, 'level'))
			loglvl = logging.__dict__[strlvl]
		except:
			loglvl = logging.WARNING

		self.LOGLEVEL = loglvl

		try:
			self.LOGOUTFILE = config.get(LOGGINGHDR, 'outfile')
			self.LOGOUTFILE = Template(self.LOGOUTFILE).substitute(**cfgvars)

			print 'Outputting log info to "{outfile}"'.format(outfile=self.LOGOUTFILE)

			logging.basicConfig(filename=self.LOGOUTFILE, \
			 format=self.LOGFORMAT, level=self.LOGLEVEL)
		except:
			self.LOGOUTFILE = None

			logging.basicConfig(format=self.LOGFORMAT, \
			 level=self.LOGLEVEL)

		# Process general alias service-related configurations;

		try:
			self.DOMAIN = config.get(ALIASHDR, 'domain')
			self.DOMAIN = Template(self.DOMAIN).substitute(**cfgvars)

		except:
			logging.warning('domain not specified in ' \
					'configuration file')
			raise

		try:
			self.MAXADDRLEN = config.getint(ALIASHDR, 'maxaddresslen')
		except:
			self.MAXADDRLEN = 254

		# Process user message handler-related configurations;

		try:
			self.USERDIR = config.get(USERMSGHDR, 'userdir')
			self.USERDIR = Template(self.USERDIR).substitute(**cfgvars)
		except:
			self.USERDIR = 'usrmsg/'

		try:
			self.ERRORDIR = config.get(USERMSGHDR, 'errordir')
			self.ERRORDIR = Template(self.ERRORDIR).substitute(**cfgvars)
		except:
			self.ERRORDIR = 'error/'

		# Process database related configurations;

		try:
			self.DBSRC = config.get(DBHDR, 'src')
			self.DBSRC = Template(self.DBSRC).substitute(**cfgvars)

		except:
			logging.warning('No database file specified in ' \
					'configuration file')
			raise

		try:
			hashname = string.lower(config.get(DBHDR, 'hashfunc'))
			self.HASHFUNC = hashlib.__dict__[hashname]
		except:
			logging.info('No existing hash function specified; ' \
				     'using md5 by default')
			self.HASHFUNC = hashlib.md5

		# Process reserved addresses;

		self.RESERVEDNAMES = set()

		for name, pfx in config.items(RESADDRHDR):
			pfx = pfx.lower()
			self.RESERVEDNAMES.add(pfx)
			self.__dict__[name.upper()] = '{0}@{1}'.format(pfx, self.DOMAIN)

		# Process alias alphabet information;

		try:
			self.RANDALPHABET = config.get(RANDSTRHDR, 'alphabet')
		except:
			self.RANDALPHABET = '123456789abcdefghjkmnpqrstuvwxyz'

		try:
			self.SEPARATORS   = config.get(RANDSTRHDR, 'separators')
		except:
			self.SEPARATORS = '._-'

		try:
			self.DEFAULTSEPARATOR = config.get(RANDSTRHDR, 'defaultseparator')
		except:
			self.DEFAULTSEPARATOR = self.SEPARATORS[0]

		# default separator must be recognizable in is_alias_name() check;
		if self.DEFAULTSEPARATOR not in self.SEPARATORS:
			self.SEPARATORS += self.DEFAULTSEPARATOR

		# Process configurations on size of randomization string;

		try:
			self.RANDLEN = config.getint(RANDSTRHDR, 'length')
			self.RANDSPACE = int(math.pow(len(self.RANDALPHABET), \
						      self.RANDLEN))
			self.RANDEXP = int(math.log(self.RANDSPACE,2))
		except:
			try:
				self.RANDEXP = config.getint(RANDSTRHDR, 'exponent')
			except:
				self.RANDEXP   = 8*5
				logging.debug('No configuration given for ' \
					      'randomization strings; ' \
					      'using default exponent value of %s',\
					      self.RANDEXP)

			self.RANDSPACE = int(math.pow(2,self.RANDEXP))
			self.RANDLEN   = int(math.ceil(self.RANDEXP / 		\
					 math.log(len(self.RANDALPHABET),2)))

		# Max alias name length is maxaddrlen less the length of the domain name, @ sign
		# randomization string, and separator;
		self.MAXALIASNAMELEN = self.MAXADDRLEN - len(self.DOMAIN) - 1 - self.RANDLEN - 1
		self.MAXUSERNAMELEN  = self.MAXADDRLEN - len(self.DOMAIN) - 1

