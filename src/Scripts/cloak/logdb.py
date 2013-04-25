import logging
import sqlite3
import os

# Didn't want to contaminate alias.cfg, so we'll store configuration info for
# logdb.'

dbpath = os.path.join(os.getenv('HOME'), 'cloak/data/logdb')
logcon = sqlite3.connect(dbpath)

def WRITE_TO_LOGDB( data, peer=None, mailfrom=None, rcpttos=None ):
	""" Logs stuff to logdb.
	CAPS is used intentionally for the function name since we may be logging
	sensitive data and this should be disabled when data collection is no
	longer needed. 
	"""
	c = logcon.cursor()

	try:
		if peer != None \
		and mailfrom != None \
		and rcpttos != None:
			rcpts = ', '.join(rcpttos)

			c.execute('INSERT INTO `mail` '	\
				'(peer, mailfrom, rcpttos, data) ' \
				'VALUES(?, ? ,?, ?)', \
				( '%s:%d'%(peer[0], peer[1] ), \
				mailfrom, rcpts, data, ) )

			logcon.commit()
			logging.debug('!#!#!#! MAIL IS LOGGED !#!#!#!')

		else:
			c.execute('INSERT INTO `mail` (data) VALUES(?)', \
				  (data,) )

			logcon.commit()
			logging.debug('!@!@!@! DATA IS LOGGED !@!@!@!')

	except sqlite3.Error, e:
		logging.debug('%s', e.args[0])

	c.close()

