#!/usr/bin/env bash 

# This script will change the superuser password on a BibOS machine.


# Expect exactly two input parameters

if [ $# -ne 2 ]
then
    echo "usage: $(basename $0) <password> <confirmation>"
    echo ""
    exit -1
fi

if [ "$1" == "$2" ]
then
    # change password
    TARGET_USER=superuser
    PASSWORD="$1"
    CRYPTPASS=$(perl -e 'print crypt($ARGV[0], "password")' $PASSWORD)
    # Done calculating, now do it.
    /usr/sbin/usermod $TARGET_USER -p $CRYPTPASS
else
    echo "Passwords didn't match!"
    exit -1
fi

exit 0



