#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import sys
import string
import random
from GmailComposer import GmailComposer

if len(sys.argv) != 8:
	print "Usage: %s <username> <password> <cloakserver> "\
		"<spamfile> <aliasfile> <bodyfile> <logfile>"
	print "username\tUsername used to log into Gmail."
	print "password\tPassword used to log into Gmail."
	print "cloaksvr\tCloak server."
	print "spamfile\tSpam data generated by fetchspam.py."
	print "aliasfile\tEntries will be cycled for use as aliasname."
	print "body\t\tEntries will be cycled for use as body text."
	print "logfile\tResults will be logged here."
	sys.exit(0)

USER = sys.argv[1]
PASSWORD = sys.argv[2]
CLOAKSERVER = sys.argv[3]
SPAMMERFILE = sys.argv[4]
ALIASFILE = sys.argv[5]
BODYFILE= sys.argv[6]
LOGFILE = sys.argv[7]

def read_cycle_file(filename, linedelim = None, fielddelim = None):
	''' Reads a file and returns an array where each element is a file
	entry. The file can be line-delimited or field-delimited.
	'''
	f = open(filename, 'r')
	array = []
	jline = ''
	line = f.readline().strip('\n')
	while line:
		if linedelim == None:
			if fielddelim == None:
				useline = line
			else:
				useline = line.split(fielddelim)
			
			array.append( useline )

		elif line == linedelim:
			# Terminator
			if fielddelim == None:
				useline = jline
			else:
				useline = jline.split(fielddelim)
			array.append(useline)
			jline = ''

		else:
			jline = jline+line

		line = f.readline().strip('\n')

	f.close()
	return array

def recoil(composer, spammer, aliasaddr, bodytext):
	''' Sends mail to spammer using the new alias.
	'''
	newsubject = "RE: "+spammer[2]
	print "%s\t%s with %s" % (aliasaddr, spammer[1], newsubject)
	tos = spammer[1] + ',' + aliasaddr
	composer.send( "Gmail - Inbox", tos, newsubject, bodytext )


# Read in cycle files (spamfile, aliasfile, and bodyfile)
SPAMFILEDELIM = '####################'
spammers = read_cycle_file(SPAMMERFILE, linedelim = SPAMFILEDELIM, fielddelim='\t')
aliases = read_cycle_file(ALIASFILE)
bodytexts = read_cycle_file(BODYFILE)

# Create a new instance of the Firefox driver
composer = GmailComposer()
composer.login(USER, PASSWORD)

# For ever spammer...
logfile = open(LOGFILE, 'a')
nbt = 0
na = 0
MAXCOUNT = 10
count = 0
for spammer in spammers:
	if count >= MAXCOUNT:
		break

	print spammer
	if spammer[3] == '1':
		continue

	#
	# Sends getalias request
	#
	firstname = aliases[random.randint(0, len(aliases) - 1)]
	lastname = aliases[random.randint(0, len(aliases) - 1)]
	fullname = string.capwords( firstname + ' ' + lastname )
	newalias = lastname + firstname[0]
	composer.send( "Gmail - Inbox", \
		'getalias@%s'%CLOAKSERVER, \
		newalias, \
		'does not matter...' )

	# Polls for getalias response
	result = composer.polls_for_mail( subjectpattern = 'Created new alias %s'%newalias )
	addrpart = string.split( result[0], ' ')[-1] 
	aliasaddr = '\"%s\" <%s>' % ( fullname, addrpart )

	# Respond to spammer
	print "Recoiling..."
	recoil( composer, spammer, aliasaddr, bodytexts[random.randint(0, len(bodytexts) - 1)])
	logfile.write("%s\t%s\n" % (addrpart.split('@')[0], spammer[1]))

	# Mark as processed
	spammer[3] = '1'

	na = (na + 1) % len(aliases)
	nbt = (nbt + 1) % len(bodytexts)
	count = count + 1

logfile.close()
composer.logout()
composer.quit()

if count > 0 :
	# Write out spammers with updated status
	f = open(SPAMMERFILE, 'w')
	for spammer in spammers:
		f.write( "%s\t%s\t%s\t%s\n%s\n" \
			% (spammer[0], spammer[1], spammer[2], spammer[3], SPAMFILEDELIM) )
	f.close()

