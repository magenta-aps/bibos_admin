#!/usr/bin/env python

# Change the startpage for Google Chrome.
# Modify the JSON in .config/google_chrome/Default/Preferences to achieve
# this.

# Synopsis: 
#    change_chrome_startpage <uri> <preferences-file>
#
# Both parameters are mandatory. The preferences-file might default to the
# user's own .config/ directory, but we'd still not know if this is Chromium or
# Chrome.
#
# There is no direct validation of the input parameters. The URI is assumed to
# be that of a valid web site, and the preferences file is assumed to exist and
# be a valid JSON file containing the Google Chrome session. 
# 
# This script will exit with an error message if any obvious errors are
# encountered, but it's generally the responsibility of the caller to supply
# sensible parameters.

import sys
import json

if len(sys.argv) != 3:
    print "Usage: change_chrome_startpage <uri> <preferences-file>"
    sys.exit(1)

uri = sys.argv[1]
preferences = sys.argv[2]

try:
    with open(preferences, 'r') as f:
        data = json.load(f)
    data['session']['urls_to_restore_on_startup'] = [uri]

    with open(preferences, 'w') as f:
        json.dump(data, f)

except Exception as e:
    print "An error occurred: " + str(e)
    sys.exit(1)



