
class Edge:

	srcnode = None
	dstnode = None
	time = None

	def __init__(self, n1, n2, time):
		self.srcnode = n1
		self.dstnode = n2
		self.time = time

	def getSource(self):
		return self.srcnode

	def getDest(self):
		return self.dstnode

	def __str__(self):
		return '%s: (%s) %s => (%s) %s' %\
			( str(self.time), self.srcnode.getName(), str(self.srcnode),\
			self.dstnode.getName(), str(self.dstnode) )
