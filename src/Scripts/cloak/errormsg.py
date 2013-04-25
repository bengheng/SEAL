
""" Class providing error message creation

	Version 0.1 created: July 25, 2011
"""

from config  import Config
from usermsg import UserMessage

cfgdata = None

class ErrorMessage(UserMessage):

	def __init__(self, msgfile, errordir=None, **keywords):

		if errordir is None:
			errordir = cfgdata.ERRORDIR

		UserMessage.__init__(self, msgfile, userdir=errordir, **keywords)
