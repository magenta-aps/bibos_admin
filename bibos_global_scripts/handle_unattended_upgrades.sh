#!/usr/bin/env bash
#
# This script will change the settings for unattended upgrades.
# This is done by parsing and patching the config files. We should really be
# using an API for handling them, but apparently people are expected to modify
# these files manually.
#
# NOTE: We will not parse the existing config file for the interval.
#       This means that if you want to change the interval e.g. from 2 to 3, 
#       you must first run the script to turn the unattended upgrades of and
#       then re-run it to turn them on with the correct interval.

APT_UNATTENDED=/etc/apt/apt.conf.d/50unattended-upgrades 
APT_PERIODIC=/etc/apt/apt.conf.d/10periodic

if [ $# -ne 2 ]
then
    echo "This script takes exactly two arguments"
    exit -1
fi

# First, find out whether to enable or disable

DO_ENABLE=$1               # Whether these should be enabled or not. 0 or the
                           # desired interval in days.
INCLUDE_DISTRIBUTIONS=$2   # What to include in automatic upgrades.
                           # This argument can take the values of "pass"
                           # (no changes), "security" (security updates only)
                           # and "all" (include normal updates).


if [ -z "$(grep Unattended-Upgrade $APT_PERIODIC | grep -v "^//")" ]
then
    IS_ENABLED=0
else
    IS_ENABLED=1
fi

#echo "Er aktiveret: $IS_ENABLED"
#echo "Skal aktiveres: $DO_ENABLE"

if [ $DO_ENABLE -gt 0 ] && [  $IS_ENABLED -eq 0 ]
then
    # Enable unattended upgrades
    echo "APT::Periodic::Unattended-Upgrade \"$DO_ENABLE\";" >> $APT_PERIODIC
fi

if [ $IS_ENABLED -eq 1 ] && [  $DO_ENABLE -eq 0 ]
then
    sed -i -e "/APT::Periodic::Unattended-Upgrade/d" $APT_PERIODIC
fi


#if [ -z "$(grep "\-security" $APT_UNATTENDED | grep -v "^//")" ]
#then
#    SECURITY_ENABLED=0
#else
#    SECURITY_ENABLED=1
#fi

if [ $INCLUDE_DISTRIBUTIONS == "security" ] || [ $INCLUDE_DISTRIBUTIONS == "all" ]
then

    # Security will always be enabled - we disable auto upgrades with the
    # IS_ENABLED parameter and the periodic file.
    #
    # From the other types of distribution we only allow "updates".

    if [ $INCLUDE_DISTRIBUTIONS == "all" ]
    then
        DO_ENABLE_UPDATES=1
    else
        DO_ENABLE_UPDATES=0
    fi

    if [ -z "$(grep "\-updates" $APT_UNATTENDED | grep -v "^//")" ]
    then
        UPDATES_ENABLED=0
    else
        UPDATES_ENABLED=1
    fi

    if [ $DO_ENABLE_UPDATES -eq 1 ] && [ $UPDATES_ENABLED -eq 0 ]
    then
        # Uncomment the line with updates
         sed -i '/-updates/ s/^\/\///' $APT_UNATTENDED
    fi

    if [ $UPDATES_ENABLED -eq 1 ] && [ $DO_ENABLE_UPDATES -eq 0 ]
    then
        # Comment out the line with updates.
         sed -i '/-updates/ s/^/\/\//' $APT_UNATTENDED
    fi
    # end if [ security or all ]
fi

exit 0
