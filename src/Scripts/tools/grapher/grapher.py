#!/usr/bin/env python

import sys
import sqlite3
import pydot
import re
import string
import hashlib

if len(sys.argv) != 3:
	print 'Usage: %s <dbloc> <graphname>' % sys.argv[0]
	sys.exit(0)

DBLOC = sys.argv[1]
OUTPUT = sys.argv[2]

def LongestCommonDomain(S1, S2):
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

def gather_domains( domain, tlds ):
	''' Consolidates list of canonicalized domains.
	'''

	# If nothing in tld, just append.
	if len(tlds) == 0:
		tlds.append(domain)
		return

	tldlen = len(tlds)

	# If there's already an entry, we're done.
	for t in range(0, tldlen):
		if domain == tlds[t]:
			return
	

	for t in range(0, tldlen):
		lcs = LongestCommonDomain( domain, tlds[t] )
	
		#print lcs
		lcslower = lcs.lower()
		if lcs != ''\
		and lcslower != 'au'\
		and lcslower != 'ca'\
		and lcslower != 'com'\
		and lcslower != 'net'\
		and lcslower != 'cn'\
		and lcslower != 'edu'\
		and lcslower != 'org'\
		and lcslower != 'info'\
		and lcslower != 'gov'\
		and lcslower != 'co.uk':
		#and isEffectiveTLD(lcs) == False:
			# If there's a LCS and it matches the
			# end of the current domain, replace
			# current domain with the LCS.
			#print "Finding \"%s\" in \"%s\"" %(lcs, tld[t])
			#obj = re.match("([a-zA-Z0-9]+\.)*"+lcs+'$', tld[t], re.M)
			obj = re.match(".*"+lcs+'$', tlds[t], re.M)
			if obj:
				tlds[t] = lcs
				return
			#else:
			#	print "No match"


	#print "2: LCS %s Appending %s"%(lcs, domain)
	# No longest common substring.
	tlds.append(domain)

def getTLD( tlds, S ):
	''' Returns TLD for S
	'''
	if S == "<>":
		return

	for t in tlds:
		obj = re.match(".*"+t+'$', S, re.M)
		if obj:
			return t
	return S


def createNode( graph, nodes, lab ):
	assert isinstance(lab, str)

	# Returns if found an existing node with same label
	for n in nodes:
		if n[0] == lab:
			return

	h = hashlib.sha1()
	if string.find( lab, '@' ) == -1:
		h.update( lab.lower() )
	else:
		h.update( lab.lower().split('@')[1] )
	hd = h.hexdigest()
	#r = (float(int(hd[:2], 16))/0xff)/2 + 0.5
	#g = (float(int(hd[2:4], 16))/0xff)/2 + 0.5
	#b = (float(int(hd[4:6], 16))/0xff)/2 + 0.5
	r = (float(int(hd[:2], 16))/0xff)
	g = (float(int(hd[2:4], 16))/0xff)
	b = (float(int(hd[4:6], 16))/0xff)
	clr = "%.2f %.2f %.2f" % (r, g, b)

	# Add new node
	newpynode = pydot.Node(lab.replace('@', '\\n'), style="filled", color=clr)
	graph.add_node(newpynode)

	newnode = (lab, newpynode)
	nodes.append(newnode)

	
def getNode( nodes, label ):
	assert isinstance(label, str)

	# Returns if found an existing node with same label
	for n in nodes:
		if n[0] == label:
			return n[1]

	return None

def createEdge( graph, edges, nodes, lab1, lab1dom, lab2, lab2dom ):
	''' Creates non-existing edge.
	'''

	# Skip existing edge
	for e in edges:
		if e[0] == lab1dom and e[1] == lab2:
			return

	# Create the nodes if they don't exist
	createNode( graph, nodes, lab1dom )
	createNode( graph, nodes, lab2 )

	# Create edge
	newpyedge = pydot.Edge( getNode(nodes, lab1dom), getNode(nodes, lab2) )
	graph.add_edge( newpyedge )

	newedge = (lab1dom, lab2) 
	edges.append( newedge )

def createNormGraph(results, tlds, graphname):
	graph = pydot.Dot(graph_type = 'digraph', overlap='false', prog='neato')

	#reduceResults( results )

	nodes = []
	edges = [] 
	for r in results:
		srcdomain = getTLD(tlds, r[0])
		dstdomain = getTLD(tlds, r[1])
		createEdge( graph, edges, nodes, r[0], srcdomain, r[1], dstdomain )

	graph.write(graphname+".dot")
	graph.write_png(graphname+".png")

#def reduceResults( results ):
#	''' All sources for the same destination will be reduced.
#	'''

#	dset = set()
#	for r in results:
#		dset.add( r[1] )

#	for ds in dset:
#		print ds
#		for r in range(0, len(results)):
#			if results[r][1] == ds:
#				# Same destination

def createGraph(results, graphname):
	graph = pydot.Dot(graph_type = 'digraph', overlap="false", prog='neato')

	nodes = []
	edges = [] 
	for r in results:
		createEdge( graph, edges, nodes, r[0], r[0], r[1], r[1] )

	graph.write(graphname+".dot")
	graph.write_png(graphname+".png")

conn = sqlite3.connect(DBLOC)
cur = conn.cursor()
cur.execute( 'SELECT `mailfrom`, `rcpttos` FROM `mail` WHERE `mailfrom` IS NOT NULL AND `rcpttos` IS NOT NULL')


tlds = []
results = []
row = cur.fetchone()
while row != None:
	src = row[0].encode('ascii', 'replace')

	# Skip mails from <> or has our own domain
	if src == "<>" or\
	src.split('@')[1] == "cloak.dyndns-mail.com":
		row = cur.fetchone()
		continue

	if src == "<>":
		# DOT format needs labels to be quoted
		# (made redundant)
		src = "\"<>\""
	else:
		gather_domains(	src.split('@')[1], tlds )

	dst = row[1].encode('ascii', 'replace')
	dstsplit = dst.split(',')
	for d in dstsplit:
		d = d.strip().rstrip()
		gather_domains( d.split('@')[1], tlds )
		results.append( [src, d] )

	row = cur.fetchone()

cur.close()
conn.close()

createGraph( results, OUTPUT )
createNormGraph( results, tlds, OUTPUT+"norm" )
