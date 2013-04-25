
""" Class for managing user information;

	Version 0.1 created: July 5, 2011
"""

import string
import logging

import config

cfgdata = None

class User(object):

	# This list should contain any columns from the 'user' table that are used
	# in the alias service code;
	userfields = ['uid',
		      'username',
		      'fwdaddr',
		      'salt',
		      'status']

	def __init__(self, **userdata):
		self.set_values(_init=True, **userdata)

	def set_values(self, _init=False, **newdata):
		""" Sets values, normally passed in by a row from the database.
		"""
		for key in self.userfields:

			if key in newdata.keys():
				self.__dict__[key] = newdata[key]
			elif _init:
				self.__dict__[key] = None

		return
		
	def get_uid(self):
		""" Returns the user's uid.
		"""
		return self.uid

	def get_username(self):
		""" Returns the user's username.
		"""
		return self.username

	def get_account_address(self):
		""" Returns the user's account address, whose local part is the
		user's user name.
		"""
		return '{localpart}@{domain}'.format(localpart	= self.username,  \
						     domain	= cfgdata.DOMAIN) 

	def get_forwarding_address(self):
		""" Returns the user's forwarding address.
		"""
		return self.fwdaddr

	def get_salt(self):
		""" Returns the user's salt, used for hashing correspondent addresses.
		"""
		return self.salt

def is_user_name(name):
	""" Performs simple check of whether this is a properly formatted username.
	"""
	if not isinstance(name,str):
		return False

	if len(name) < 1 or len(name) > cfgdata.MAXUSERNAMELEN:
		logging.debug('username "%s" too long! %d characters, max is %d.', \
				name, len(name), cfgdata.MAXUSERNAMELEN)
		return False

	# user name cannot be a reserved address, or there would be a
	# conflict;
	if name.lower() in cfgdata.RESERVEDNAMES:
		return False

	# user name must be alphanumeric string;
	for c in name:
		if not (c in string.letters or c in string.digits):
			return False

	return True

