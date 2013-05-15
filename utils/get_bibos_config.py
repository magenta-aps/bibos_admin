#!/usr/bin/env python

import sys
sys.path.append("/usr/share/bibos/bibos_admin")

from utils.bibos_config import get_config

args = len(sys.argv)
val = None

try:
    if args > 2:
        val = get_config(sys.argv[1], sys.argv[2])
    else:
        val = get_config(sys.argv[1])
except:
    pass

if val is not None:
    print val
