#!/usr/bin/env bash 

# This script will place a shortcut on the desktop of a BibOS machine.
#
# Instructions:
#    - Create a shortcut by whatever means necessary. 
#    - If you want to put e.g. a PDF file or a movie clip at the user's
#      disposal, you can just use the file as parameter for this script.
#    - If it's a program or URL shortcut, you MUST create a .desktop file.
#      Refer to the documentation for instructions about how to do this.
#    - Run this script and specify the file you wish to place on the desktop as
#      first and only parameter.
#    - The audience user must log out and log in again for your changes to take
#      effect.


# Check input.

if [ $# -ne 1 ]
then
    echo "usage: $(basename $0) {filename}"
    echo ""
    exit -1
fi

# Now check the input file actually exists

DESKTOP_FILE=$1

if [ ! -f $DESKTOP_FILE ]
then
    echo "No such file: $DESKTOP_FILE"
    echo "Please supply a path to an existing settings file"
    exit -1
fi


cp $DESKTOP_FILE /home/.skjult/Desktop

exit 0



