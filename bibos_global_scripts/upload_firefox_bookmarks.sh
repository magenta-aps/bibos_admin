#!/usr/bin/env bash

# This file will take one argument, a new bookmarks backup file, and place it
# in the user's Mozilla Firefox profile, thus changing the bookmarks.
# 
# No attempt is made to verify that the file in question actually contains
# valid Firefox bookmarks - that is the responsibility of the user of the
# script.

if [ ! $# -eq 1 ] 
then
    echo "This script takes exactly one argument"
    exit -1
fi

FIREFOX_BOOKMARKS=$1
BOOKMARKS_DIR="/home/.skjult/.mozilla/firefox/e1362422.default/bookmarkbackups"


if [ -f $FIREFOX_BOOKMARKS ]
then
    mkdir -p $BOOKMARKS_DIR
    cp $FIREFOX_BOOKMARKS $BOOKMARKS_DIR
else
    echo "Please specify an existing bookmarks file."
    exit -1
fi




