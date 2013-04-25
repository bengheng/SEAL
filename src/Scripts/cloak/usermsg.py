
""" Class providing user message creation

	Version 0.1 created: July 25, 2011
"""

import email.message
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

import logging
from string import Template
import os

from config  import Config
from message import Message
import time

cfgdata = None

class UserMessage(Message):

	def __init__(self, msgfile, userdir=None, images=None, **keywords):

		Message.__init__(self)
		msgheaders = []

		if userdir is None:
			userdir = cfgdata.USERDIR

		try:
			f = open(os.path.join(userdir, msgfile), 'r')

			# File can start with comments, denoted by a starting # sign;
			curline = f.readline()
			while curline and curline[0].strip() == '#':
				curline = f.readline()

			# Then comes the header fields, concluded with a '--' line;
			while curline and curline.strip() != '--':
				curline = curline.strip()

				headerpair = curline.split(':',1)

				if len(headerpair) == 2:
					hdrname, hdrval = headerpair

					hdrname = hdrname.strip()

					hdrval  = hdrval.strip()
					hdrval  = Template(hdrval).safe_substitute(**keywords)

					msgheaders.append( (hdrname, hdrval) )

					curline = f.readline()
				else:
					logging.warning('User message "%s" contains improperly formatted '
							'header: "%s"', msgfile, curline)
					raise

			# The rest will be the message body;
			if curline:
				msgdata = f.read().strip()
				msgdata = Template(msgdata).safe_substitute(**keywords)

			else:
				msgdata = ""

		except:
			logging.info('Could not open user message file')
			raise

		# Compose user response message;
		if images == None:
			rawmsg = MIMEText(msgdata)
		else:
			txtmsg = MIMEText(msgdata)
			rawmsg = MIMEMultipart()
			rawmsg.attach(txtmsg)
			# Attach images
			for imgfile in images:
				# image paths should probably be taken relative to userdir;
				# imgfile = os.path.join(userdir, imgfile)
				fp = open(imgfile, 'rb')
				img = MIMEImage(fp.read())
				fp.close()
				rawmsg.attach(img)

		self.set_payload(rawmsg.get_payload())
		for hdr in rawmsg.keys():
			self.add_header(hdr, rawmsg[hdr])

		for hdr in msgheaders:
			self.add_header(*hdr)

