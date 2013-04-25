#!/usr/bin/env python

import os
import sys
import email
import getopt
import datetime
from collections import Counter

def ProcEmail(mail):
	#print msg.get('From')
	#print msg.keys()
	#print msg.get('From')
	#tos = msg.get_all('to', [])
	#print email.utils.getaddresses(tos)
	print mail.get('Date') + '\t' + email.utils.formatdate(email.utils.mktime_tz(email.utils.parsedate_tz(mail.get('Date'))))

#=======================================================================
def BinByTo(emails, tolist, to_bin):
	'''
	Sorts the emails according to TO field.
	'''

	for t in tolist:
		cnt = Counter()
	
		# Get 'From' field of all emails sent to t
		for m in emails:
			tos = m.get_all('to', [])
			toaddrs = email.utils.getaddresses(tos)
			if toaddrs[0][1].startswith(t) or \
			toaddrs[1][1].startswith(t):
				cnt[email.utils.parseaddr(m.get('From'))[1]] += 1

		to_bin.append(cnt)


	assert( len(to_bin) == len(tolist) )
	print to_bin
	for n in range(0, len(to_bin)):
		b = to_bin[n]
		#di = dict(b)
		#print '%s\t%s' % (tolist[n], str(di))
		print '%s,%s' % (tolist[n], len(list(b.elements())))

#=======================================================================

def GetDateRange(emails):
	# Get earliest date
	edate = datetime.datetime(*email.utils.parsedate_tz(emails[0].get('Date'))[0:7])
	ldate = edate
	for mail in emails[1:]:
		mdate = datetime.datetime(*email.utils.parsedate_tz(mail.get('Date'))[0:7])
		if mdate < edate:
			edate = mdate
		if mdate > ldate:
			ldate = mdate

	return (edate, ldate)

def BinByDate(emails, edate, date_bin):
	'''
	Sorts the emails according to date.
	'''

	(ed, ld) = GetDateRange(emails)

	if edate == None:
		edate = ed
	ldate = ld

	maxdays = (ldate - edate).days
	print "From %s through %s. Max days %d" % (edate, ldate, maxdays)

	for b in range(0, maxdays+1):
		date_bin.append(0);
		

	for mail in emails:
		mdate = datetime.datetime(*email.utils.parsedate_tz(mail.get('Date'))[0:7])
		timedelta = mdate - edate
		date_bin[timedelta.days] = date_bin[timedelta.days] + 1

	print date_bin

#=======================================================================

def IsInTolist(tolist, to):
	for t in tolist:
		if to.startswith(t):
			return True
	return False 

def IsAcceptedTos(mail, tolist):
	'''
	Return TRUE If email has valid TO fields. TO fields are valid if there are 2 entries,
	one of which is 'smithsonjohan@cloak.dyndns-mail.com' and the other being an entry
	in tofile.
	'''

	tos = mail.get_all('to', [])
	toaddrs = email.utils.getaddresses(tos)

	m = 'smithsonjohan@cloak.dyndns-mail.com'
	if len(toaddrs) == 2 and \
	((toaddrs[0][1] == m and IsInTolist(tolist, toaddrs[1][1])) or \
	(toaddrs[1][1] == m and IsInTolist(tolist, toaddrs[0][1]))):
			return True

	return False

def GetValidTos(tofile, tolist):
	'''
	Gets list of valid TOs.
	'''
	f = open(tofile, 'r')

	l = f.readline().strip()
	while l != '':
		tolist.append(l)
		l = f.readline().strip()

	f.close()	


def AddEmail(mailstr, emails):
	'''
	Performs necessary checks on the email message,
	and if OK, add to emails list.
	'''
	mail = email.message_from_string(mailstr)
	if IsAcceptedTos(mail, tolist):
		emails.append(mail)

def GetEmails(infile, emails, tolist):
	'''
	Extracts emails from file.
	'''
	f = open(infile, 'r')

	mailstr = ''
	l = f.readline()
	while True:
		if l == '':
			AddEmail(mailstr, emails)
			break

		if l.startswith('From - '):
			if mailstr != '':
				AddEmail(mailstr, emails)
			mailstr = l
		else:
			mailstr += l

		l = f.readline()

	f.close()	

#=======================================================================

def PrintUsage():
	print 'Usage: %s -f <infile> -l <tofile> [-d <startdate YYYY-MM-DD>]' % sys.argv[0]
	sys.exit(0)

optlist, args = getopt.getopt(sys.argv[1:], 'f:l:d:')
infile = ''
tofile = ''
edate = None

for opt in optlist:
	if opt[0] == '-f':
		infile = os.path.realpath(opt[1])
	elif opt[0] == '-l':
		tofile = os.path.realpath(opt[1])
	elif opt[0] == '-d':
		edate = datetime.datetime.strptime(opt[1], '%Y-%m-%d')
	else:
		print 'Ignoring unknown option \"%s\"' % opt

if infile == '' or tofile == '':
	PrintUsage()
elif not os.path.exists(infile):
	print 'Cannot find %s.' % infile
	PrintUsage()
elif not os.path.exists(tofile):
	print 'Cannot find %s.' % tofile
	PrintUsage()

tolist = []
GetValidTos(tofile, tolist)

emails = []
GetEmails(infile, emails, tolist)

date_bin = []
BinByDate(emails, edate, date_bin)

to_bin = []
#BinByTo(emails, tolist, to_bin)
