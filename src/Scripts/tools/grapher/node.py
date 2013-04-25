import re

class Node:

	email = None
	localpart = None
	fulladdr = None
	domain = None
	affiliationid = None
	nid = None

	def __init__(self, nid, email):
		self.email = email
		self.nid = nid

		(self.localpart, self.fulladdr) = email.split('@')

	def setAffiliation(self, domaffiliations):
		''' Sets affiliationid based on domain.
		domaffiliations is a dictionary that maps affiliation
		ids to list of domains.

		Returns True if successful.
		'''

		# Goes through all domain affiliations.
		# If there's a match, assign affiliation id.
		for affid, domains in domaffiliations.iteritems():
			for d in domains:
				if re.match( '.*'+d+'$', self.fulladdr, re.M ):
					# Found match
					self.domain = d
					self.affiliationid = affid
					return True

		return False

	def __str__(self):
		return self.email

	def getName(self):
		return 'n'+str(self.nid)
