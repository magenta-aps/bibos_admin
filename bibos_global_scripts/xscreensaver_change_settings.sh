#!/usr/bin/env bash 

# This is a very simple script to change the audience user's screensaver
# settings on a BibOS machine.
#
# Instructions:
#    - Configure the screensaver as you want it on an existing machine
#    - Run this script and specify your .xscreensaver file as input parameter
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

SETTINGS_FILE=$1

if [ ! -f $SETTINGS_FILE ]
then
    echo "No such file: $SETTINGS_FILE"
    echo "Please supply a path to an existing settings file"
    exit -1
fi

# We don't validate this is a real settings file, so please don't shoot
# yourself in the foot.

cp $SETTINGS_FILE /home/.skjult/.xscreensaver

exit 0



