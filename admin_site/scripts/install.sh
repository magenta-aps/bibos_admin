#!/usr/bin/env bash

# Setup virtualenv, install packages necessary to run BibOS Admin.
# System requirements, installed packages etc. are checked 
# in a separate dependencies file. 

if [ -e ./bin/activate ]
then
    echo "virtual environment already installed" 1>&2
    exit
fi

virtualenv .
source bin/activate

DIR=$(dirname ${BASH_SOURCE[0]})
PYTHON_PACKAGES=$(cat "$DIR/PYTHON_DEPENDENCIES")

for  package in "${PYTHON_PACKAGES[@]}"
do
    pip install $package

    RETVAL=$?
    if [ $RETVAL -ne 0 ]; then
        echo "" 1>&2
        echo "ERROR: Unable to install Python package <$package>." 1>&2
        echo -n "Please check your network connection. " 1>&2
        echo "A remote server may be down - please retry later. " 1>&2
        echo "" 1>&2
        exit -1
    fi
done


