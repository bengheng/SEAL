#!/usr/bin/env python

import os
import sys
import getopt
import sqlite3
import traceback
import base64
from Crypto.Cipher import AES

# Parse input arguments
optlist, args = getopt.getopt( sys.argv[1:], 'e:d:p:o:' )
encrypt = None
dbiname = ''
dboname = ''
password = 'YmVuZ2FsZXhhdHVs'

# Base 64 encoding for 'atulalexbeng'
initval = 'YXR1bGFsZXhiZW5n'

for opt in optlist:
	if opt[0] == '-e':
		encrypt = True
		dbiname = os.path.realpath( opt[1] )

	elif opt[0] == '-d':
		encrypt = False
		dbiname = os.path.realpath( opt[1] )

	elif opt[0] == '-o':
		dboname = os.path.realpath( opt[1] )

	elif opt[0] == '-p':
		password = opt[1]

	else:
		print 'Ignoring unknown option \"%s\"' % opt

if encrypt == None or dbiname == '' or \
	dboname == '' or password == '':
	print 'Usage: %s -<e|d> <dbiname> -o <dboname> -p <password>' % sys.argv[0]
	sys.exit(0)

if not os.path.exists( dbiname ):
	print 'Input database does not exist.'
	sys.exit(0)

if not os.path.exists( dboname ):
	print 'Output database does not exist.'
	sys.exit(0)

#
# AES encrypt, Base 64 encode
#

def encb64( plaintext, password, initval ):
	if plaintext == None:
		return None

	while (len(plaintext) % 16) != 0:
		plaintext += '\n'

	aes = AES.new(password, AES.MODE_CBC, initval)
	#aes = AES.new(password, AES.MODE_ECB)
	ciphertext = aes.encrypt(plaintext)
	return base64.b64encode(ciphertext)

def encrypt_row( dbo, row, password, initval ):
	# mailfrom
	encmailfrom = encb64( row[2], password, initval )	

	# rcpttos
	encrcpttos = encb64( row[3], password, initval )	

	# data
	encdata = encb64( row[4], password, initval )

	# Update row
	curo = dbo.cursor()
	curo.execute( 'INSERT INTO mail '
			'(`mid`,`peer`,`mailfrom`,`rcpttos`,`data`,`timestamp`) '
			'VALUES (?,?,?,?,?,?)',
			(row[0], row[1], encmailfrom,
			encrcpttos, encdata, row[5],) )

	dbo.commit()
	curo.close()

#
# Base 64 decode, AES decrypt
#

def decb64( b64ciphertext, password, initval ):
	if b64ciphertext == None:
		return None

	ciphertext = base64.b64decode(b64ciphertext)
	aes = AES.new(password, AES.MODE_CBC, initval)
	#aes = AES.new(password, AES.MODE_ECB)
	plaintext = aes.decrypt(ciphertext)

	plaintext = plaintext.rstrip('\n')

	return plaintext

def decrypt_row( dbo, row, password, initval ):
	# mailfrom
	mailfrom = decb64( row[2], password, initval )

	# rcpttos
	rcpttos = decb64( row[3], password, initval )

	# data
	data = decb64( row[4], password, initval )

	curo = dbo.cursor()
	curo.execute( 'INSERT INTO mail '
			'(`mid`,`peer`,`mailfrom`,`rcpttos`,`data`,`timestamp`) '
			'VALUES (?,?,?,?,?,?)',
			(row[0], row[1], mailfrom,
			rcpttos, data, row[5],) )

	dbo.commit()
	curo.close()

dbo = sqlite3.connect(dboname)
dbi = sqlite3.connect(dbiname)
curi = dbi.cursor()

try:
	curi.execute( 'SELECT * FROM mail;' )
	row = curi.fetchone()
	while row:
		if encrypt == True:
			encrypt_row( dbo, row, password, initval )
		elif encrypt == False:
			decrypt_row( dbo, row, password, initval )
		row = curi.fetchone()

except sqlite3.DatabaseError:
	print 'Unexpected Database Error: ', sys.exc_info()[0]
	traceback.print_exc(file = sys.stdout)

curi.close()
dbi.close()
dbo.close()
