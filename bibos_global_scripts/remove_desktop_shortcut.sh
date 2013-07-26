#!/usr/bin/env bash

if [ $# -ne 1 ]
then
    echo "This script takes exactly one parameter"
    exit -1

fi

FILENAME=$1

rm -f "/home/.skjult/Desktop/$FILENAME"

exit 0
