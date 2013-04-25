
""" Class representing an email message, with added header manipulation
 capabilities;

	Version 0.1 created: July 5, 2011
"""

# WARNING:| Some functions from the parent class may not work as expected given the
# AHH!!!! | changes in this extended class.  Mainly any that rely on the value of
# WARNING | headers, as the headers list and the headers in the Message object
# AHH!!!! | are not always synchronized. Any functions redefined below should work
# WARNING | properly however, which I believe is everything.

import email.message
import logging

import address
from address import Address

# Used to check whether argument is a function in search_header_addresses()
function = type(lambda: None)

class Message(email.message.Message):

	headers = []	# alias_hdrs_changed must be set
			# to True after any direct modification;

	msg_hdrs_changed   = False;
	alias_hdrs_changed = False;

	def __init__(self):

		self.msg_hdrs_changed   = False;
		self.alias_hdrs_changed = False;

		email.message.Message.__init__(self)

	def unload_headers(self):
		""" Unload the headers from the parent into easily accessible list.
		"""
		self.headers = []

		# Headers not easily accessible through the python APIs, so
		# they're loaded into the "headers" list for easy access and
		# pushed back onto the message later
		for hdr in email.message.Message.items(self):
			self.headers.append(list(hdr))

		self.msg_hdrs_changed = False

		return

	def reload_headers(self):
		""" Wipe the old headers and apply our modified ones from the "headers" list.
		"""
		for hdr in self.headers:
			email.message.Message.__delitem__(self, hdr[0])

		for hdr in self.headers:
			email.message.Message.add_header(self, *hdr)

		self.alias_hdrs_changed = False

		return

	def generate_message_id(self, domain):
		""" Creates a random message-id and appends it to this message's headers.
		"""
		import random
		import string

		if self.alias_hdrs_changed:
			self.reload_headers()

		rstr = ''
		for i in range(50):
			rstr += random.choice(string.letters + string.digits + '+=-_')

		msgid = '<{rand}@{domain}>'.format(rand=rstr,	\
						   domain=domain)

		self['Message-ID'] = msgid

		self.msg_hdrs_changed = True

		return

	def get_header_addresses(self, fieldname):
		""" Returns a list of Address objects representing all address entries
		in the given field.
		"""
		return address.getaddresses(self.get_all(fieldname))

	def get_header_length(self, fieldname):
		""" Returns the number of addresses in the given field.
		"""
		return len(self.get_header_addresses(fieldname))

	def search_header_addresses(self, fieldname, searchfunc):
		""" Searches all headers of the given field name for the first address
		under which the passed search function returns True;

		searchfunc must take in a tuple (x,y) parsed RFC822 header address, where
		x is the text associated with address y and return a boolean result; or
		searchfunc can be a string which is matched against each address in the
		field;
		"""
		if self.msg_hdrs_changed:
			self.unload_headers()
		
		fname = fieldname.lower()

		for hdr in self.headers:
			if fname == hdr[0].lower():

				phdr = address.getaddresses([hdr[1]])

				for entry in phdr:
					if (isinstance(searchfunc,function)	\
					   and searchfunc(entry))		\
					   or (entry.address == searchfunc):
						yield entry
		return

	def replace_address(self, fieldname, saddx, daddx):
		return self._replace_addresses(fieldname, saddx, daddx)

	def replace_all_addresses(self, fieldname, saddx, daddx):
		return self._replace_addresses(fieldname, saddx, daddx, \
					       replace_all=True)

	def remove_address(self, fieldname, saddx):
		return self._replace_addresses(fieldname, saddx, None)

	def _replace_addresses(self, fieldname, saddx, daddx, replace_all=False):

		if self.msg_hdrs_changed:
			self.unload_headers()

		fname = fieldname.lower()

		for hdr in self.headers:
			if fname == hdr[0].lower():

				phdr = address.getaddresses([hdr[1]])
				replaced_any = False

				for i in range(len(phdr)):
					if (phdr[i] == saddx) or (saddx is None):

						if daddx is not None:
							phdr[i].set_address(str(daddx))
						else:
							del phdr[i]

						replaced_any = True

						if not replace_all:
							break

				if replaced_any:
					hdr[1] = ', '.join(map(str,phdr))
					self.alias_hdrs_changed = True

		return True

	def as_string(self, unixfrom=False):
		if self.alias_hdrs_changed:
			self.reload_headers()

		alias_unixfrom = unixfrom
		return email.message.Message.as_string(self, \
						       unixfrom=alias_unixfrom)

	def __str__(self):
		if self.alias_hdrs_changed:
			self.reload_headers()

		return email.message.Message.__str__(self)

	def __len__(self):
		if self.alias_hdrs_changed:
			return len(headers)

		return email.message.Message.__len__(self)

	def __contains__(self, name):
		if self.alias_hdrs_changed:
			self.reload_headers()

		return email.message.Message.__contains__(self, name)

	def __getitem__(self, name):
		if self.alias_hdrs_changed:
			self.reload_headers()

		return email.message.Message.__getitem__(self, name)

	def __setitem__(self, name, val):
		if self.alias_hdrs_changed:
			self.reload_headers()

		self.msg_hdrs_changed = True
		return email.message.Message.__setitem__(self, name, val)

	def __delitem__(self, name):
		if self.alias_hdrs_changed:
			self.reload_headers()

		self.msg_hdrs_changed = True
		return email.message.Message.__delitem__(self, name)

	def has_key(self, name):
		if self.alias_hdrs_changed:
			self.reload_headers()

		return email.message.Message.has_key(self, name)

	def keys(self):
		if self.alias_hdrs_changed:
			self.reload_headers()

		return email.message.Message.keys(self)
	
	def values(self):
		if self.alias_hdrs_changed:
			self.reload_headers()

		return email.message.Message.values(self)

	def items(self):
		if self.alias_hdrs_changed:
			self.reload_headers()

		return email.message.Message.items(self)

	def get(self, name, failobj=None):
		if self.alias_hdrs_changed:
			self.reload_headers()

		alias_failobj = failobj
		return email.message.Message.get(self, name, failobj=alias_failobj)

	def get_all(self, name, failobj=None):
		if self.alias_hdrs_changed:
			self.reload_headers()

		alias_failobj = failobj
		return email.message.Message.get_all(self, name, \
						     failobj=alias_failobj)

	def add_header(self, _name, _value, **_params):
		if self.alias_hdrs_changed:
			self.reload_headers()

		self.msg_hdrs_changed = True
		return email.message.Message.add_header(self, _name, _value, \
							**_params)

	def replace_header(self, _name, _value):
		if self.alias_hdrs_changed:
			self.reload_headers()

		self.msg_hdrs_changed = True
		return email.message.Message.replace_header(self, _name, _value)
