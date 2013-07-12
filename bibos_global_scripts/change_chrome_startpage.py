#!/usr/bin/env python

# Change the startpage for Google Chrome.
# Modify the JSON in .config/google_chrome/Default/Preferences to achieve
# this.

# Synopsis: 
#    change_chrome_startpage <uri> [<preferences-file>]
#
# The URI is mandatory. The preferences-file defaults to the .config/
# directory in the hidden user directory in a standard BibOS installation.
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

if len(sys.argv) == 2:
    preferences = '/home/.skjult/.config/google-chrome/Default/Preferences'
elif len(sys.argv) == 3:
    preferences = sys.argv[2]
else:
    print "Usage: change_chrome_startpage <uri> [<preferences-file>]"
    sys.exit(1)

uri = sys.argv[1]

try:
    with open(preferences, 'r') as f:
        data = json.load(f)
    data['session']['urls_to_restore_on_startup'] = [uri]
    data['session']['restore_on_startup'] = 4

    with open(preferences, 'w') as f:
        json.dump(data, f)

except Exception as e:
    print "An error occurred: " + str(e)
    sys.exit(1)



