#!/usr/bin/python

import sys
from cloak.config import Config
import cloak.alias

# Redirect stdout to stderr
savedstdout = sys.stdout
sys.stdout = sys.stderr

# Initialize configurations
cfg = Config('/home/john/cloak/src/Scripts/alias.cfg')
cloak.alias.cfgdata = cfg
# Generate random integer
if len(sys.argv) == 2:
	rint = int( sys.argv[1] )
else:
	rint = cloak.alias.generate_rint()
rstr = cloak.alias.rint_to_rstr(rint)

# Retore stdout
sys.stdout = savedstdout

# Write output
sys.stdout.write(str(rint)+","+rstr)

