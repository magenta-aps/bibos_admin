#!/usr/bin/env bash

# This file will take one argument, which is an image file to replace the 
# current warning icon on the user's desktop.
#
# It is the uploader's responsibility to ensure the new file is formatted
# correctly etc.
# 

if [ ! $# -eq 1 ] 
then
    echo "This script takes exactly one argument"
    exit -1
fi

NEW_WARNING=$1
TARGET_PATH="/usr/share/bibos/icons/Advarsel.svg"


if [ -f $NEW_WARNING ]
then
    cp $NEW_WARNING $TARGET_PATH
else
    echo "Please specify an existing bookmarks file."
    exit -1
fi




