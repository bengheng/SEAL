#!/usr/bin/env python

# Script that generates a GDF file for the GUESS
# graph exploration system.

import os
import sys
import getopt
import string
import sqlite3
import node
import edge
import time
from datetime import datetime

def printUsage():
	print "Usage: %s -d <db location> -a <affiliation file> -g <gdf file>" % sys.argv[0]
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

def loadAffiliations( aff_file, domaffliations ):
	''' Load domain affiliations from file.
	'''
	f = open(aff_file, 'r')

	n = 1
	l = f.readline().strip()
	while l:
		domaffiliations[n] = string.split(l, ',')
		n = n + 1
		l = f.readline().strip()

	f.close()

def addNode( nodes, email ):
	''' Adds node if one doesn't already exist.
	If the node already exist, returns it. Otherwise,
	returns the new node.
	'''
	for n in nodes:
		if str(n) == email:
			# Already exist
			return n

	newnode = node.Node( len(nodes), email)
	nodes.append( newnode )
	return newnode

def loadDB( db, nodes, edges ):
	''' Load data from database.
	'''

	conn = sqlite3.connect( db )
	cur = conn.cursor()

	cur.execute( 'SELECT `mailfrom`, `rcpttos`, `timestamp` FROM `mail` '\
		'WHERE `mailfrom` IS NOT NULL AND `rcpttos` IS NOT NULL' )

	row = cur.fetchone()
	while row != None:
		src = row[0].encode('ascii', 'replace')

		if src == '<>':
			row = cur.fetchone()
			continue

		# Add src node
		snode = addNode( nodes, src )


		# There could be several destination
		# email addresses.
		dst = row[1].encode('ascii', 'replace')
		dstsplit = dst.split(',')
		for d in dstsplit:
			d = d.strip().rstrip()

			# Add dst node
			dnode = addNode( nodes, d )

			# Get timestamp in Epoch seconds
			dt = int(time.mktime( datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S').timetuple() ))

			# Add edge
			edges.append( edge.Edge(snode, dnode, dt) )

		row = cur.fetchone()

	cur.close()
	conn.close()

def dumpGDF( nodes, edges, gdf_file ):
	''' Dumps nodes and edges to gdf file.
	'''

	f = open( gdf_file, 'w+' )

	# Write nodes
	f.write( 'nodedef> name,email VARCHAR(128),localpart VARCHAR(64),fulladdr VARCHAR(128),'\
		'domain VARCHAR(64),affid INT\n' )
	for n in nodes:
		f.write( n.getName() +\
			',' + n.email +\
			',' + n.localpart +\
			',' + n.fulladdr +\
			',' + n.domain +\
			',' + str(n.affiliationid) + '\n' )

	# Write edges
	f.write( 'edgedef> node1,node2,directed,timestamp INT\n' )
	for e in edges:
		n1 = e.getSource()
		n2 = e.getDest()
		f.write( n1.getName() + \
			',' + n2.getName() + \
			',1' +\
			',' + str(e.time) + '\n' )
	
	f.close()

db = None
aff_file = None
gdf_file = None

optlist, args = getopt.getopt( sys.argv[1:], 'a:d:g:' )

# Gets user options.
for opt in optlist:
	if opt[0] == '-d':
		db = os.path.realpath( opt[1] )
		if isValidDB( db ) == False:
			sys.exit(0)
	elif opt[0] == '-a':
		aff_file = os.path.realpath( opt[1] )
		if os.path.exists(aff_file) == False:
			print "Affiliation file does not exist!"
			sys.exit(0)
	elif opt[0] == '-g':
		gdf_file = os.path.realpath( opt[1] )
		if os.path.exists(gdf_file) == True:
			print "GDF file already exist!"
			sys.exit(0)
	else:
		print "Ignoring unknown option \"%s\"" % opt

if aff_file == None or gdf_file == None:
	printUsage()

domaffiliations = dict()
loadAffiliations( aff_file, domaffiliations )
print "%d items in dict" % len(domaffiliations)

nodes = []
edges = []
loadDB( db, nodes, edges )
print "Added %d nodes, %d edges" % (len(nodes), len(edges))

# Set affiliations for all nodes
for n in nodes:
	if n.setAffiliation( domaffiliations ) == False:
		print "Error: No affiliation for "+str(n)
		sys.exit(0)

print "Dumping GDF"
dumpGDF( nodes, edges, gdf_file )
