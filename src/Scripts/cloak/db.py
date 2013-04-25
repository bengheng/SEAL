
""" Class of functions for interacting with the database.

	NOTE:
	1. AliasData should not be too tightly coupled with
	other classes. It should only perform it's main task,
	which is to interface with the database, and do that well.
	For example, it should not be responsible for updating
	fields in Alias class.

	2. To make the code more readable, the following coding
	guidelines should be followed:

	http://bayes.colorado.edu/PythonGuidelines

	Version 0.1 created: July 5, 2011
"""

import sqlite3
import logging
from inspect import currentframe

#from config import Config
#from address import Address

class DB(object):

	CONTACT_ALLOW	= 0
	CONTACT_DENY	= 1

	CLIST_DENIED	= 0
	CLIST_APPROVED	= 1

	CAPTCHA_NONE		= 0
	CAPTCHA_PENDING		= 1
	CAPTCHA_APPROVED	= 2
	USER_PENDING		= 2

	_dbconn	= None
	_hash_method = None

	def __init__(self, cfg):
		try:
			self._dbconn = sqlite3.connect(cfg.DBSRC)
			self._dbconn.row_factory = sqlite3.Row
		except: raise

		self._hash_method = cfg.HASHFUNC

	def __del__(self):
		if self._dbconn:
			self._dbconn.close()

	def hash_data(self, data, salt):
		""" The consistent hash function used for storing hashed, salted
		data in our alias service databases.
		"""
		return self._hash_method(data + salt).hexdigest()

	def insert_alias(self, uid, aliasname, isprimary=False):
		""" Inserts alias for user into DB and returns new alias id.
		"""
		lastid = None
		c = self._dbconn.cursor()

		try:
			c.execute('INSERT OR IGNORE INTO alias (uid, aliasname, isprimary) ' \
				  'VALUES (?, ?, ?)', (uid,aliasname,isprimary))

			lastid = c.lastrowid

			if not lastid:
				logging.info('Alias creation failed; "%s" already taken', \
						aliasname)
				return None

			self._dbconn.commit()
			c.close()

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		return lastid

	def insert_aliasrnd(self, uid, aid, aliasname, aliasrand, \
	isactive, istrusted=True, hint=None, domain=None):
		""" Inserts aliasrand for user into DB and returns new rid.
		"""
		lastid = None
		c = self._dbconn.cursor()

		try:
			c.execute('INSERT INTO aliasrnd '\
				'(uid, aid, aliasname, aliasrand, isactive, istrusted, hint, domain) '\
				'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',\
				(uid, aid, aliasname, aliasrand, isactive, istrusted, hint, domain))

			lastid = c.lastrowid
			self._dbconn.commit()

			c.close()

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		return lastid 

	def get_alias_data(self, aliasarg1, aliasrand=None, **extras):
		""" Returns alias data from DB with optional restrictions;
		Takes either just the rid or an alias pair along with
		extra restrictions specified by the extras dictionary.
		"""
		c = self._dbconn.cursor()

		query = 'SELECT * FROM aliasrnd WHERE '

		# Construct restrictions to query;
		if aliasrand is None:
			restrictions = ['rid']
			params = [aliasarg1]
			baseargc = 1
		else:
			restrictions = ['aliasname', 'aliasrand']
			params = [aliasarg1, aliasrand]
			baseargc = 2

		restrictions.extend(extras.keys())

		# Construct tuple to pass into query;
		params.extend(map(lambda x: extras[x], restrictions[baseargc:]))
		params = tuple(params)

		# Add restrictions to query string;
		restrictions = map(lambda x: x+'=?', restrictions)
		query += ' AND '.join(restrictions)

		try:
			c.execute(query, params)

			alias_data = c.fetchone()

			if alias_data is None:
				debugstr = ' AND '.join(map(lambda x,y: x[0:-1]+str(y),
							    restrictions[baseargc:], params[baseargc:]))

				if aliasrand is None:
					logging.info('Failed to find alias (rid=%s) in '\
						     'table aliasrnd with restrictions '\
						     '"%s".',				\
						     aliasarg1, debugstr)

				else:
					logging.info('Failed to find alias (%s,%s) in '	\
						     'table aliasrnd with restrictions '\
						     '"%s".',				\
						     aliasarg1, aliasrand, debugstr)

				c.close()

				return None

			assert c.fetchone() is None

			c.close()

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		return alias_data

	def get_aliasname_data(self, aliasname):
		""" Returns (aid, uid) tuple  for aliasname.
		"""
		c = self._dbconn.cursor()
		aid = None
		uid = None

		try:
			c.execute('SELECT aid, uid FROM alias '		\
				  'WHERE aliasname=?', (aliasname,))

			res = c.fetchone()
			aid = int(res[0]) if res else None
			uid = int(res[1]) if res else None
			c.close()

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		return (aid, uid)

	def get_aliases(self, uid):
		""" Returns a list of aliases using uid.
		"""
		results = []
		c = self._dbconn.cursor()

		try:
			c.execute('SELECT aliasname, aliasrand FROM aliasrnd '	\
				  'WHERE uid=?', (uid,))

			r = c.fetchone()
			while r is not None:
				results.append( r )
				r = c.fetchone()

			c.close()

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		return results

	def infer_alias(self, uid, correspondents, salt):
		""" Attempts to infer the alias to use given a list of correspondents
		and the uid of the user.
		"""
		c = self._dbconn.cursor()

		try:
			candaliases = set()

			for cspdt in correspondents:

				cur_cid = self.peek_cid(cspdt, salt)

				if not cur_cid:
					continue

				c.execute('SELECT rid, aliasname, aliasrand '	\
					  'FROM aliasrnd WHERE rid IN '		\
					  '(SELECT rid FROM history '		\
					  'WHERE cid=?) AND uid=?',		\
					   (cur_cid, uid))

				for row in c:
					candaliases.add(row)

			c.close()

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		if len(candaliases) != 1:
			return False

		return candaliases.pop()

	def is_trusted_correspondent(self, cspdt, salt, rid, timestamp):
		""" Returns whether the given correspondent is in the trusted group
		for the alias represented by rid, based on the given timestamp.
		"""
		c = self._dbconn.cursor()

		try:
			cid = self.peek_cid(cspdt, salt)

			if not cid:
				return False

			c.execute('SELECT hid FROM history WHERE rid=? '\
				  'AND cid=? AND timestamp<?',		\
				   (rid, cid, timestamp))

			# just need to know that there's at least one such entry;
			res = c.fetchone()

			# if there isn't, try the whitelist as a last resort;
			if res is None:
				c.execute('SELECT status FROM control_list '	\
					  'WHERE cid=? AND rid=?',		\
					  (cid, rid))

				res = c.fetchone()

				assert c.fetchone() is None

				c.close()

				if res is None:
					return False

				return res['status'] == self.CLIST_APPROVED

			c.close()

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		return res != None

	def set_untrusted_alias(self, uid, hashmsgid):
		""" Marks all of the user's aliases as untrusted, using the earliest
		timestamp corresponding to the message with the given message-id.
		Returns the number of aliases that were marked as untrusted (which
		could in rare cases be > 1).
		"""
		timestamp = None
		res = 0
		c = self._dbconn.cursor()

		logging.debug('looking for hmid %s', hashmsgid)

		try:
			c.execute('SELECT rid, timestamp FROM '	\
				  'history WHERE hashmsgid=? '	\
				  'ORDER BY timestamp ASC',	\
				  (hashmsgid,))

			temp = 0
			for row in c:
				temp = temp + 1
				logging.debug('found history entry to act on')

				if timestamp is None:
					timestamp = row['timestamp']

				# truststamp cannot be increased.  Otherwise, user
				# might accidentally increase it if the message
				# happens to involve multiple aliases;
				c.execute('UPDATE aliasrnd SET istrusted=0, '		\
					  'truststamp=? WHERE rid=? AND uid=? '		\
					  'AND (truststamp is NULL OR truststamp>=?)',	\
					  (timestamp, row['rid'], uid, timestamp))

				assert c.rowcount >= 0
				logging.debug('rows changed this iteration: %d', c.rowcount)

				res += c.rowcount

			self._dbconn.commit()

			c.close()

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		logging.debug('found %d entries to loop over', temp)
		logging.debug('set %d aliases as untrusted', res)

		return res

	def get_user(self, uid=None, username=None):
		""" Fetches the user data corresponding to the given
		uid or username (should never need to specify both).
		"""
		c = self._dbconn.cursor()

		query = 'SELECT * FROM user WHERE '

		if uid:
			query += 'uid=?'
			params = (uid,)

		elif username:
			query += 'username=?'
			params = (username,)

		else:
			logging.debug('No criteria specified in call to db.get_user()')
			return False

		try:
			c.execute(query, params)

			userdata = c.fetchone()

			if userdata is None:
				c.close()
				return False

			assert c.fetchone() is None

			c.close()

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		return userdata

	def get_history_rid(self, aliasname, cid):
		""" Returns the last rid from the history table for the cid.
		"""
		rid = None
		row = None
		c = self._dbconn.cursor()

		try:
			#c.execute('SELECT rid FROM history '			\
			#	'WHERE cid=? ORDER BY rid DESC', (cid,))
	
			c.execute('SELECT a.rid FROM aliasrnd as a, history as h '\
				'WHERE a.aliasname=? AND h.cid=? AND '		\
				'a.rid = h.rid ORDER BY a.rid DESC',		\
				(aliasname, cid))
			row = c.fetchone()
	
			#if c.fetchone() != None:
			#	logging.warning('ERROR: Multiple rid results '	\
			#			'for cid %d', cid)
			#	c.close()
			#	return None

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',				\
				currentframe().f_code.co_filename,		\
				currentframe().f_lineno,			\
				e.args[0])
		c.close()

		if row != None:
			rid = row[0]

		return rid 

	def peek_cid(self, contact, salt):
		""" Returns cid for the given contact/salt if it exists.
		Will not create a new one (as opposed to get_cid).
		"""
		cid = None

		c = self._dbconn.cursor()

		hashed_contact = self.hash_data(contact.address, str(salt))

		try:
			c.execute('SELECT cid FROM contact '		\
				  'WHERE hashcontact=?', (hashed_contact,))

			row = c.fetchone()

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		c.close()

		if row is not None:
			cid = row[0]

		return cid 

	def get_cid(self, contact, salt):
		""" Returns cid for the given contact/salt, creating a new
		one if it did not previously exist. Hence this function will
		always return a cid.
		"""
		hashed_contact = self.hash_data(contact.address, str(salt))

		cid = self.peek_cid(contact, salt)

		if cid:
			return cid

		c = self._dbconn.cursor()

		try:
			c.execute('INSERT OR IGNORE INTO contact '	\
				  '(hashcontact) VALUES (?)',		\
				  (hashed_contact,))

			cid = c.lastrowid

			self._dbconn.commit()
			c.close()

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		assert cid is not None

		return cid

	def add_history(self, rid, is_sender, correspondents, msgid, salt):
		""" Inserts records of correspondence for the alias with the given rid
		with the correspondent addresses passed in the corresponents list
		"""
		c = self._dbconn.cursor()

		sendval = 1 if is_sender else 0
		hashmsgid = self.hash_data(msgid, str(salt))

		try:
			# For each correspondent, get/create their cid
			# and insert their entry into history;
			for cspdt in correspondents:
				cid = self.get_cid(cspdt, salt)

				c.execute('INSERT INTO history (rid, issender, cid, '	\
					  'hashmsgid, timestamp) '			\
					  'VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)',	\
					  (rid, sendval, cid, hashmsgid))

			self._dbconn.commit()
			c.close()

		except sqlite3.Error, e:
			logging.fatal('%s\t%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		return True

	def allow_sender(self, uid, identifier):
		''' Checks parameters and sets the control list to allow the given
		sender
		'''
		c = self._dbconn.cursor()

		try:
			c.execute('SELECT rid, cid, identifier, capstat FROM captcha '	\
				  'WHERE identifier=?',		\
				  (identifier,))

			row = c.fetchone()

			if c.fetchone():
				return False

			adata = self.get_alias_data(row['rid'])

			# alias must belong to user;
			if not (adata and adata['uid']==uid):
				return False

			c.execute('INSERT INTO control_list (cid, rid, status) '	\
				  'VALUES (?,?,?)',				\
				  (row['cid'], row['rid'], self.CLIST_APPROVED))

			assert c.rowcount == 1

			self._dbconn.commit()

			c.close()

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		return True

	def get_capstat(self, contact, salt, rid):
		""" Returns (cid, capstat) for hashed_contact.
		capstat has the following values:
		0 - CAPTCHA_NONE
		1 - CAPTCHA_PENDING
		2 - CAPTCHA_APPROVED
		"""
		c = self._dbconn.cursor()
		row = None

		cid = self.peek_cid(contact, salt)

		if not cid:
			return self.CAPTCHA_NONE

		try:
			c.execute('SELECT cid, capstat FROM captcha '	\
				  'WHERE cid=? AND rid=?',		\
				  (cid, rid))

			row = c.fetchone()

			assert c.fetchone() == None

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		c.close()

		if not row:
			return self.CAPTCHA_NONE

		return row['capstat']

	def set_capstat(self, cid, rid, capstat):
		''' Sets capstat flag for cid.
		'''

		c = self._dbconn.cursor()


		try:
			c.execute('UPDATE `captcha` SET `capstat`=? '	\
				  'WHERE `cid`=? AND `rid`=?',		\
				  (capstat, cid, rid))

			if c.rowcount == 0:
				c.execute('INSERT INTO captcha (cid, rid, capstat) '	\
					  'VALUES (?,?,?)',				\
					  (cid, rid, capstat))

			self._dbconn.commit()

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		return

	def delete_captcha_identifier(self, identifier):
		''' Deletes identifier in CAPTCHA table.
		'''

		c = self._dbconn.cursor()
		try:
			c.execute('DELETE FROM `captcha` WHERE identifier=?', (identifier,))
			self._dbconn.commit()

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		c.close()
		return

	def replace_captcha_identifier(self, oldidentifier, newidentifier, word):
		''' Replaces captcha entries having the specified identifier
		with the new identifier and word.
		'''

		c = self._dbconn.cursor()
		try:
			c.execute('SELECT capid FROM `captcha` WHERE identifier=?', (oldidentifier,))

			# Replace identifier and word
			r = c.fetchone()
			while r != None:
				logging.debug( 'Updating capid %d', r[0] )
				c2 = self._dbconn.cursor()
				c2.execute('UPDATE `captcha` SET identifier=?, word=? '\
				'WHERE capid=?', (newidentifier, word, r[0],))
				c2.close()
				r = c.fetchone()
			self._dbconn.commit()

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		c.close()
		return

	def set_captcha(self, identifier, word, cid, rid, capstat):
		''' Sets captcha word and identifier.
		'''

		c = self._dbconn.cursor()
		try:
			c.execute('UPDATE captcha SET identifier=?, word=?, capstat=?'	\
				  'WHERE cid=? AND rid=?',			\
				  (identifier, word, capstat, cid, rid))

			if c.rowcount == 0:
				c.execute('INSERT INTO captcha (cid, rid, identifier, word, capstat) '	\
					  'VALUES (?,?,?,?,?)',				\
					  (cid, rid, identifier, word, capstat))

			self._dbconn.commit()

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		c.close()
		return

	def get_captcha_word(self, identifier):
		''' Sets captcha word and identifier.
		'''
		c = self._dbconn.cursor()

		try:
			c.execute('SELECT `cid`, `rid`, `word` FROM `captcha` WHERE `identifier`=?',\
				(identifier,))

			row = c.fetchone()

			assert c.fetchone() is None

			c.close()

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		return row

	def insert_websession(self, uid, sessionkey):
		''' Inserts sessionkey.
		'''

		lastid = None
		c = self._dbconn.cursor()

		try:
			c.execute('INSERT INTO `websession` (`uid`, `sessionkey`) '\
				'VALUES(?,?)', (uid, sessionkey))
			lastid = c.lastrowid

			if not lastid:
				logging.info('Error inserting sessionkey for uid ', uid)
				return None

			self._dbconn.commit()

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',			\
				currentframe().f_code.co_filename,	\
				currentframe().f_lineno,		\
				e.args[0])

		c.close()
		return lastid

	def get_websession(self, uid, wid):
		''' Gets websession.
		'''
		row = None
		c = self._dbconn.cursor()

		try:
			c.execute('SELECT sessionkey FROM websession '			\
				'WHERE wid=? AND uid=?', (wid, uid))
	
			row = c.fetchone()
	
			#if c.fetchone() != None:
			#	logging.warning('ERROR: Multiple rid results '	\
			#			'for cid %d', cid)
			#	c.close()
			#	return None

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',				\
				currentframe().f_code.co_filename,		\
				currentframe().f_lineno,			\
				e.args[0])
		c.close()

		return row

	def get_primary_alias(self, uid):
		''' Gets primary alias for uid.
		'''
		row = None
		c = self._dbconn.cursor()

		try:
			c.execute('SELECT aid, aliasname FROM alias '			\
				'WHERE uid=? AND isprimary=1 ORDER BY aid DESC', (uid,))
	
			row = c.fetchone()
	
			#if c.fetchone() != None:
			#	logging.warning('ERROR: Multiple rid results '	\
			#			'for cid %d', cid)
			#	c.close()
			#	return None

		except sqlite3.Error, e:
			logging.fatal('%s:%d\t%s',				\
				currentframe().f_code.co_filename,		\
				currentframe().f_lineno,			\
				e.args[0])
		c.close()

		return row

