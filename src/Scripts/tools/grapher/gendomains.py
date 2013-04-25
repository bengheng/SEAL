#!/usr/bin/env python

# Script to extract domains from database and outputs to a file
# in a format which the user can specify domain affiliations.

import os
import re
import sys
import string
import getopt
import sqlite3

def printUsage():
	print "Usage: %s -d <dbloc> -o <affiliation file>" % sys.argv[0]
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

def longestCommonDomain(S1, S2):
	''' Returns longest common domain.
	'''
	s1 = S1.split('.')
	s2 = S2.split('.')

	s1len = len(s1)
	s2len = len(s2)

	uselen =  min(s1len, s2len)

	lcd = ''
	for i in range(0, uselen):
		if s1[-1-i] == s2[-1-i]:
			if lcd == '':
				lcd = s1[-1-i]
			else:
				lcd = s1[-1-i] + '.' + lcd

	return lcd

def gatherDomains( domain, domains ):
	''' Consolidates list of canonicalized domains.
	'''

	# If nothing in domains, just append.
	if len(domains) == 0:
		domains.append(domain)
		return

	domlen = len(domains)

	# If there's already an entry, we're done.
	for t in range(0, domlen):
		if domain == domains[t]:
			return
	

	for t in range(0, domlen):
		lcd = longestCommonDomain( domain, domains[t] ).lower()
	
		if lcd != ''\
		and lcd != 'au'\
		and lcd != 'ca'\
		and lcd != 'com'\
		and lcd != 'net'\
		and lcd != 'cn'\
		and lcd != 'edu'\
		and lcd != 'org'\
		and lcd != 'info'\
		and lcd != 'gov'\
		and lcd != 'co.uk':
			# If there's a LCD and it matches the
			# end of the current domain, add to domains.
			obj = re.match(".*"+lcd+'$', domains[t], re.M)
			if obj:
				domains[t] = lcd
				return
			#else:
			#	print "No match"

	# No longest common substring.
	domains.append(domain)

def readDomainsFromDB( db, domains ):
	''' Read domains from database.
	'''

	conn = sqlite3.connect(db)
	cur = conn.cursor()
	cur.execute( 'SELECT `mailfrom`, `rcpttos` FROM `mail` '\
		'WHERE `mailfrom` IS NOT NULL AND `rcpttos` IS NOT NULL')	

	row = cur.fetchone()
	while row != None:
		src = row[0].encode('ascii', 'replace')

		# Skip mails from <>. These are mails that do not
		# have a "from" address in the envelope. Cloak now
		# replaces such address with that of the message
		# "from" field.
		if src == "<>":
			row = cur.fetchone()
			continue

		gatherDomains(	src.split('@')[1], domains )

		dst = row[1].encode('ascii', 'replace')
		dstsplit = dst.split(',')
		for d in dstsplit:
			d = d.strip().rstrip()
			gatherDomains( d.split('@')[1], domains )

		row = cur.fetchone()

	cur.close()
	conn.close()

def writeSingleDomainToAffiliationFile( domain, affile ):
	''' Write one domain to affiliation file.
	'''

	if os.path.exists( affile ):
		f = open( affile, 'r+' )

		l = f.readline().strip()
		while l != '':
			token = string.split(l, ',')
			for t in token:
				t = t.strip().rstrip()

				# If the domain is already in the file,
				# return.
				if t == domain:
					f.close()
					return False

			l = f.readline().strip()

		f.close()

	# Didn't find domain in file.
	# Reopen file for appending.
	f = open( affile, 'a' )
	f.write( domain+'\n' )
	f.close()
	return True


def writeDomainsToAffiliationFile( domains, affile ):
	''' Write domains to affiliation file.
	'''

	n = 0
	for d in domains:
		if writeSingleDomainToAffiliationFile( d, affile ) == True:
			n = n + 1

	print 'Wrote %d domains.' % n

db = ""
affile = ""
optlist, args = getopt.getopt( sys.argv[1:], 'd:o:' )

# Gets user options.
for opt in optlist:
	if opt[0] == '-d':
		db = os.path.realpath( opt[1] )
		if isValidDB( db ) == False:
			sys.exit(0)
	elif opt[0] == '-o':
		affile = os.path.realpath( opt[1] )
	else:
		print "Ignoring unknown option \"%s\"" % opt

if db == "" or affile == "":
	printUsage()

domains = []
readDomainsFromDB( db, domains )
writeDomainsToAffiliationFile( domains, affile )
