#!/usr/bin/env bash

# This script will change the user's Firefox startup page to the URL given
# argument. There will be no validation that this parameter is a valid URL.

if [ $# -ne 1 ]
then
    echo "This script takes exactly one argument."
    exit -1
fi

NEW_START_PAGE=$1
STARTPAGE_PREFS_LINE="user_pref(\"browser.startup.homepage\", \"$1\");"
PREFS_FILE="/home/.skjult/.mozilla/firefox/e1362422.default/prefs.js"

# Remove existing start page, if any
sed -i "/browser.startup.homepage\>/ d" $PREFS_FILE

echo $STARTPAGE_PREFS_LINE >> $PREFS_FILE


