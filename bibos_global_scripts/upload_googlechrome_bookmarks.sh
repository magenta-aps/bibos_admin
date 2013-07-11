#!/usr/bin/env bash

# This file will take one argument, a new bookmarks backup file, and place it
# in the user's Google Chrome profile, thus changing the bookmarks.
# 
# No attempt is made to verify that the file in question actually contains
# valid Firefox bookmarks - that is the responsibility of the user of the
# script.

if [ ! $# -eq 1 ] 
then
    echo "This script takes exactly one argument"
    exit -1
fi

CHROME_BOOKMARKS=$1
BOOKMARKS_FILE="/home/.skjult/.config/google-chrome/Default/Bookmarks"


if [ -f $CHROME_BOOKMARKS ]
then
    cp $CHROME_BOOKMARKS $BOOKMARKS_FILE
else
    echo "Please specify an existing bookmarks file."
    exit -1
fi




