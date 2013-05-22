
import sys

from bibos_config import set_config

args = len(sys.argv)
val = None

if args > 3:
    set_config(sys.argv[1], sys.argv[2], sys.argv[3])
else:
    if args > 2:
        set_config(sys.argv[1], sys.argv[2])
    else:
        sys.stderr.write("Too few arguments\n")
        sys.exit(1)
