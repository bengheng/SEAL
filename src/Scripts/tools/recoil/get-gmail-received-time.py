#!/usr/bin/env python

import imaplib
import email
import string
import sys
import getopt
import re
import time
import datetime

def usage():
	print 'Usage: %s -u <username> -p <password> -o <outfname>' % sys.argv[0]

def list_mboxes(c):
	typ, data = c.list()
	print 'Response code:', typ
	print len(data)
	for d in data:
		print str(d)

def get_state(s):
	''' There are 5 possible states:
		1. Non-SEAL => Non-SEAL
		2. Non-SEAL => SEAL
		3. SEAL => SEAL
		4. SEAL => Non-SEAL
		5. ? => Non-SEAL
	'''

	if s.find('from') == -1:
		return 5

	domain = 'cloak.dyndns-mail.com'
	p1 = 'from %s' % domain
	p2 = 'by %s' % domain
	r1 = s.find(p1)
	r2 = s.find(p2)
	if r1 == -1 and r2 == -1:   return 1
	elif r1 == -1 and r2 != -1: return 2
	elif r1 != -1 and r2 != -1: return 3
	elif r1 != -1 and r2 == -1:	return 4

	return -1

def get_time(date_re, s):
	''' Extract time data from the input string.
	'''

	# Try using email.utils first.
	datestr = s.split(',')[-1]
	if datestr == s:
		datestr = s.split(';')[-1]
	datestr = datestr.strip()
	parsedate = email.utils.parsedate_tz(datestr)

	# If email.utils doesn't work, use regex.
	if parsedate == None:
		datesearch = re.search(date_re, s)
		if datesearch == None:
			return None
		datestr = datesearch.group(0)
		parsedate = email.utils.parsedate_tz(datestr)

	# Give up if still can't parse date
	if parsedate == None:
		return None

	t = email.utils.mktime_tz(parsedate)
	return datetime.datetime.utcfromtimestamp(t)

def get_timedelta_seconds(td):
	return ((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6)

def get_mails_in_folder(mail, folder, time_offset, out):
	''' Returns a list of folders.
	'''
	mail.select(folder)

	date_pattern = '[0-3]?[0-9]{1} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}\s?[+|-]*[0-9]*\s?[\(]?\w*[\)]?'
	date_re = re.compile(date_pattern)

	status, data = mail.search(None, 'ALL')
	for num in data[0].split():
		status, data = mail.fetch(num, '(BODY.PEEK[HEADER] FLAGS)')
		m = email.message_from_string(data[0][1])

		print m['Subject']
		prevst = -1
		currst = -1
		prevtime = None
		currtime = None
		l = m.get_all('Received')
		if l == None:
			continue
		l.reverse()
		for a in l:
			a = re.sub('\015', '', a)
			a = re.sub('\012', '', a)
			#if a == '(from nobody@localhost)' or a.startswith('from unknown'):
			#	continue
			print a
			currtime = get_time(date_re, a)
			if currtime == None:
				continue

			currst = get_state(a)

			if currst == 2 or currst == 3:
				currtime = currtime - time_offset

			#print str(prevst) + '=>' + str(currst) + ' \"'+ a +'\"'

			if prevst != -1 and currst != -1:
				print a
				print '\t' + a.split(',')[-1].strip()
				print '\t\t' + str(prevst) + '=>' + str(currst)
				print '\t\t' + str(prevtime) + ' => ' +	str(currtime)

				delta = currtime - prevtime
				if prevst == 1 and currst == 1:
					print '\t\t\t1 ' + str(delta)
					out.write('1,'+str(get_timedelta_seconds(delta))+'\n')
				elif prevst == 1 and currst == 2:
					print '\t\t\t2 ' + str(delta) 
					out.write('2,'+str(get_timedelta_seconds(delta))+'\n')
				elif prevst == 2 and currst == 3:
					print '\t\t\t3 ' + str(delta) 
					out.write('3,'+str(get_timedelta_seconds(delta))+'\n')
				elif prevst == 3 and currst == 4:
					print '\t\t\t4 ' + str(delta) + ' ' + str(get_timedelta_seconds(delta))
					out.write('4,'+str(get_timedelta_seconds(delta))+'\n')
				elif prevst == 4 and currst == 1:
					print '\t\t\t5 ' + str(delta)
					out.write('4,'+str(get_timedelta_seconds(delta))+'\n')
				elif prevst == 5 and currst == 2:
					print '\t\t\t6 ' + str(delta)
					out.write('6,'+str(get_timedelta_seconds(delta))+'\n')
				elif prevst == 5 and currst == 1:
					print '\t\t\t7 ' + str(delta)
					out.write('7,'+str(get_timedelta_seconds(delta))+'\n')
				elif prevst == 1 and currst == 5:
					print '\t\t\t8 ' + str(delta)
					out.write('8,'+str(get_timedelta_seconds(delta))+'\n')
				elif prevst == 4 and currst == 5:
					pass
				elif prevst == 5 and currst == 5:
					pass
				else:
					assert False, 'Unthinkable! prevst = %d   currst = %d' % (prevst, currst)

				#print str(datetime.datetime.utcfromtimestamp(delta))
				#print str(delta)
				print '---------------------'

			prevtime = currtime
			prevst = currst

		print '========================='
		# break

	mail.close()

if __name__ == '__main__':
	username = None
	password = None
	outfname = None
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'u:p:o:', ['username', 'password', 'outfname'])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(-1)

	for o, a in opts:
		if o in ('-u', '--username'):
			username = a
		elif o in ('-p', '--password'):
			password = a
		elif o in ('-o', '--outfname'):
			outfname = a
		else:
			assert False, 'Ignoring unknown option \"%s\"' % o

	if username == None or password == None or outfname == None:
		usage()
		sys.exit(-1)

	# Login to Gmail and select Spam folder
	mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
	mail.login(username, password)

	# List mboxes
	#list_mboxes(mail)

	out = open(outfname, 'w')
	time_offset = datetime.timedelta(seconds = 94)
	get_mails_in_folder(mail, '[Gmail]/Spam', time_offset, out)
	get_mails_in_folder(mail, '[Gmail]/All Mail', time_offset, out)
	#get_mails_in_folder(mail, 'Mailing Lists/Cint', time_offset, out)

	out.close()
	mail.logout()
else:
	print 'DEBUG'
