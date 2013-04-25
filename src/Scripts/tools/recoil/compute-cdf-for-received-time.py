#!/usr/bin/env python

from __future__ import division
import getopt
import sys
import math

def usage():
	print 'Usage: %s -i <infname> -o <outfname>' % sys.argv[0]

if __name__ == '__main__':
	infname = None
	outfname = None

	try:
		opts, args = getopt.getopt(sys.argv[1:], 'i:o:', ['infname', 'outfname'])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(-1)

	for o, a in opts:
		if o in ('-i', '--infname'):
			infname = a
		elif o in ('-o', '--outfname'):
			outfname = a
		else:
			assert False, 'Ignoring unknown option \"%s\"' % o

	if infname == None or outfname == None:
		usage()
		sys.exit(-1)


	ty3_min = None
	ty3_max = None
	ty3_combined_secs = 0
	ty3_count = 0
	combined_secs = 0
	count = 0
	histo = {}
	infile = open(infname, 'r')
	line = infile.readline().strip('\n')
	while line:
		tystr, secstr = line.split(',')
		sec = int(secstr)
		if sec < 0:
			line = infile.readline().strip('\n')
			continue

		# doesn't make sense to have 0 sec delay.
		#sec = sec + 1

		# Gather stats for type 3
		if tystr == '3':
			if ty3_min == None or sec < ty3_min:
				ty3_min = sec
			if ty3_max == None or sec > ty3_max:
				ty3_max = sec
			ty3_combined_secs = ty3_combined_secs + sec
			ty3_count = ty3_count + 1

		# Increment count
		count = count + 1
		combined_secs = combined_secs + sec
		if sec not in histo.keys():
			histo[sec] = 1
		else:
			histo[sec] = histo[sec] + 1

		line = infile.readline().strip('\n')

	infile.close()

	if ty3_min != None:
		print 'Minimum: %d' % ty3_min
	if ty3_max != None:
		print 'Maximum: %d' % ty3_max
	print 'Total Sec: %d' % ty3_combined_secs
	print 'Total Count: %d' % ty3_count
	if ty3_count != 0:
		ty3_average = ty3_combined_secs / ty3_count
		print 'Average: %f' % (ty3_average)
	print 'Cumu: %d' % count

	# Output histogram to outfile
	cumulation = 0
	mean = combined_secs / count
	outfile = open(outfname, 'w')
	variance = 0
	for key in sorted(histo.iterkeys()):
		print '[%d] = %d' % (key, histo[key])
		ratio = histo[key]/count
		cumulation = cumulation + ratio
		variance = variance + ((key - mean) *  (key - mean) * ratio)
		outfile.write('%d %d %f %f\n' % (key, histo[key], histo[key]/count, cumulation))
		#for i in range(0, histo[key]):
		#	outfile.write('%d\n' % (key))

	stddev = math.sqrt(variance)
	numsds = abs(ty3_average - mean) / stddev
	print 'Mean: %f' % mean
	print 'Variance: %f' % variance
	print 'Stddev: %f' % stddev
	print 'Num of Stddevs: %f' % numsds
	outfile.close()
