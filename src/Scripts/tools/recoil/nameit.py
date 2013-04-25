#!/usr/bin/env python

import string
import random
import sys

if len(sys.argv) != 2:
	print 'Usage: %s <namefile>' % sys.argv[0]
	sys.exit(0)

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


namearray = read_cycle_file( sys.argv[1] )

firstname = namearray[random.randint(0, len(namearray) - 1)]
lastname = namearray[random.randint(0, len(namearray) - 1)]
fullname = string.capwords( firstname + ' ' + lastname )
print fullname

