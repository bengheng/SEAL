#!/usr/bin/env python

import os
import sys
import getopt
import sqlite3
import datetime
import time

def printUsage():
	print "Usage: %s -d <dbloc> -a <aliasrnd>" % sys.argv[0]
	sys.exit(0)

def isValidDB( db ):
	''' Returns True if database exists and passes integrity check.
	'''
	if os.path.exists( db ) == False:
		print "Missing database file \"%s\"!" % db
		return False

	conn = sqlite3.connect( db )
	cur = conn.cursor()
	try:
		cur.execute( "PRAGMA integrity_check;" )
	except sqlite3.DatabaseError:
		print "Database fails integrity check!"
		cur.close()
		conn.close()
		return False
	
	cur.close()
	conn.close()

	return True

def rstr_to_rint(rstr):
	""" Converts from the "base 32" randomization string format to integer form.
	"""
	RANDALPHABET = "123456789abcdefghjkmnpqrstuvwxyz"

	rint = 0
	exponent = 1

	if not(isinstance(rstr,str)) or len(rstr) != 8:
		return False

	rstr = rstr.lower()

	for i in range(8):
		try:
			rchar = RANDALPHABET.index(rstr[-1-i])
		except ValueError:
			return False
		rint = rint + exponent*rchar
		exponent = exponent * len(RANDALPHABET)

	return rint

def getCountOnDay( db, aliasrand, date ):
	dt1 = int(time.mktime( date.timetuple() ))

	# Add 1 day
	date2 = date + datetime.timedelta(1)
	dt2 = int(time.mktime( date2.timetuple() ))

	conn = sqlite3.connect(db)
	cur = conn.cursor()

	aliasname = aliasrand.split('.')[0]
	rint = rstr_to_rint( aliasrand.split('.')[1] )
	# print rint

	cur.execute( 'SELECT COUNT(*) FROM `history` AS h, `aliasrnd` AS a WHERE '\
		'a.aliasname = ? AND '\
		'a.aliasrand = ? AND '\
		'a.rid = h.rid AND '\
		'h.issender = 0 AND '\
		'h.timestamp BETWEEN ? AND ?', ( aliasname, rint, date, date2, ) )

	row = cur.fetchone()
	sys.stdout.write(str(row[0]))

	cur.close()
	conn.close()

db = ""
aliasrnd = ""
optlist, args = getopt.getopt( sys.argv[1:], 'd:a:' )

# Gets user options.
for opt in optlist:
	if opt[0] == '-d':
		db = os.path.realpath( opt[1] )
		if isValidDB( db ) == False:
			sys.exit(0)
	elif opt[0] == '-a':
		aliasrnd = os.path.realpath( opt[1] )
		if os.path.exists(aliasrnd) == False:
			printUsage()
	else:
		print "Ignoring unknown option \"%s\"" % opt

if db == "" or aliasrnd == "":
	printUsage()




startdate = datetime.date( 2011, 7, 17)


arfile = open(aliasrnd, 'r')
line = arfile.readline().rstrip()
while line:
	sys.stdout.write( line + ' ' )

	for i in range(0,35):
		if i != 0:
			sys.stdout.write(' ')
		delta = datetime.timedelta(i)
		curdate = startdate + delta
		getCountOnDay( db, line, curdate)

	sys.stdout.write( '\n' )
	line = arfile.readline().rstrip()

