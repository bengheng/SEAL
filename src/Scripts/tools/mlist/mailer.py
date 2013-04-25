#!/usr/bin/env python

from GmailComposer import GmailComposer
import sys
import random
import time
import string

if len(sys.argv) != 8:
	print "Usage: %s <username> <password> <cloaksvr> <aliasefile> <bodyfile> <listfile> <logfile>"
	print "username\tUsername used to log into Gmail."
	print "password\tPassword used to log into Gmail."
	print "cloaksvr\tCloak server."
	print "aliasfile\tEntries will be cycled for use as aliasname."
	print "bodyfile\tEntries will be cycled for use as body text."
	print "listfile\tFile containing mailing list emails and commands."
	print "logfile\t\tResults will be logged here."
	sys.exit(0)

USER = sys.argv[1]
PASSWORD = sys.argv[2]
CLOAKSERVER = sys.argv[3]
ALIASFILE = sys.argv[4]
BODYFILE= sys.argv[5]
LISTFILE = sys.argv[6]
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

# Read in alias and body file
aliases = read_cycle_file(ALIASFILE)
bodytexts = read_cycle_file(BODYFILE)
lists = read_cycle_file(LISTFILE, fielddelim = '\t')

logfile = open(LOGFILE, 'a')
composer = GmailComposer()
composer.login(USER, PASSWORD)
MAXSEND = 10
sent = 1
for l in lists:
	#
	# Check number of mails sent
	#
	if sent > MAXSEND:
		break

	exists = False
	#
	# If list is already in LOGFILE, skip
	#
	f = open(LOGFILE, 'r')
	for line in f:
		if '%s\t%s' % (l[0], l[1]) in line:
			exists = True
			break
	f.close()
	if exists == True:
		print 'Skipping \"%s %s\". Exists.' % (l[0], string.split(l[1], ' ')[1])
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

	#
	# Polls for getalias response
	#
	result = composer.polls_for_mail( subjectpattern = 'Created new alias %s'%newalias )
	#result = ['Created new alias dummy.12345678@cloak.eecs.umich.edu']
	addrpart = string.split( result[0], ' ')[-1] 
	aliasaddr = '\"%s\" <%s>' % ( fullname, addrpart )

	#
	# Prepares to send subscription
	#
	tos = l[0] + ',' + aliasaddr
	subject = '%s %s' % (l[1], fullname)
	body = subject


	#
	# Send subscription
	#
	print "%d Sending subscription email..." % sent
	composer.send( "Gmail - Inbox", tos, subject, body)
	logentry = '%s\t%s\t%s' % (addrpart, l[0], subject)
	logfile.write("%f\t%s\n" % (time.time(), logentry) )

	sent = sent + 1

logfile.close()
composer.logout()
composer.quit()
