#!/usr/bin/env python

from BeautifulSoup import BeautifulSoup
import urllib
import sys

if len(sys.argv) != 2:
	print "Usage: %s <listfile>"
	print "listfile\tOutput file."
	sys.exit(0)

def get_list_info( url ):
	f = urllib.urlopen( url )
	s = f.read()
	f.close()

	soup = BeautifulSoup( s )
	a = soup('a', {'name' : 'SUB'})[0]
	email = a.nextSibling.text
	command = a.parent.nextSibling.pre.text
	return (email, command)


# Get a file-like object for the Python Web site's home page.
f = urllib.urlopen("http://www.lsoft.com/scripts/wl.exe?XS=10000")
# Read from the object, storing the page's contents in 's'.
s = f.read()
f.close()


listfile = open(sys.argv[1], 'w+')
soup = BeautifulSoup(s)
dtTag = soup('dt')
for dt in dtTag:
	#print dt
	children = dt.findChildren('a')

	mailinglist = get_list_info( 'http://www.lsoft.com'+children[0]['href'] )
	listfile.write( '%s\t%s\n' % (mailinglist[0], mailinglist[1]) )

listfile.close()
