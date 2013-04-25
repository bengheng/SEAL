#!/usr/bin/env python

"""
Fetches mails from Gmail's Spam folder/tag.
"""

import imaplib
import email
import string
import sys

if len(sys.argv) < 4:
	print "Usage: %s <username> <password> <spamfile> [ignore]"
	print "username\tUsername used to log into Gmail."
	print "password\tPassword used to log into Gmail."
	print "spamfile\tSpam data."
	print "ignore\t\t(Optional) List of strings to be ignored if "\
		"found in \"From\" or \"Subject\" header."
	sys.exit(0)

USER = sys.argv[1]
PASSWORD =  sys.argv[2]
SPAMFILE = sys.argv[3]
if len(sys.argv) == 5:
	IGNORE = sys.argv[4]

#
# Read in spamfile
#
SPAMFILEDELIM = '####################'
spammers = []
try:
	f = open(SPAMFILE, 'r')
	jline = ''
	line = f.readline().strip('\n')
	while line:
		if line == SPAMFILEDELIM:
			# Terminator
			spammers.append( jline.split('\t') )
			jline = ''
		else:
			jline = jline + line
		line = f.readline().strip('\n')
	f.close()
except:
	print "Can't load data from spamfile \"%s\"." % SPAMFILE

print "Loaded %d spammers." % len(spammers)

#
# Reads ignore list
#
ignore = []
if len(sys.argv) == 5:
	igfile = open(IGNORE, 'r')
	l = igfile.readline()
	while l:
		l = string.replace( l, '\n', '').replace( '\r', '' )
		ignore.append(l)
		l = igfile.readline()
	igfile.close()


# Login to Gmail and select Spam folder
mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
mail.login(USER, PASSWORD)
mail.select('[Gmail]/Spam')

# Fetches mails
f = open(SPAMFILE, 'a')
n = 0
status, data = mail.search(None, 'ALL')
for num in data[0].split():
	#status, data = mail.fetch(num, '(RFC822)')
	# This doesn't mark the mail as SEEN
	status, data = mail.fetch(num, '(BODY.PEEK[HEADER] FLAGS)')
	m = email.message_from_string(data[0][1])

	# Checks against ignore
	ignored = False
	for i in ignore:
		if string.find(m["From"], i) != -1 \
		or string.find(m["Subject"], i) != -1:
			ignored = True
			break

	# Message ID must not already exist
	for spammer in spammers:
		if m["Message-Id"] == spammer[0]:
			ignored = True
			break
		
	if ignored == False:
		subject = m["Subject"]
		subject = string.replace(subject, '\n', '\\n')
		subject = string.replace(subject, '\r', '\\r')
		subject = string.replace(subject, '\t', '\\t')
		# Writes to file
		out = '%s\t%s\t%s\t0\n%s\n' \
			% (m["Message-Id"], m["From"], subject, SPAMFILEDELIM)
		f.write(out)
		n = n +1


f.close() 
print "Wrote %d new spammers." % n
mail.close()
mail.logout()

