#!/usr/bin/env bash

# This is a script to make a BibOS machine shutdown at a certain time.
#
# Synopsis: 
#     
#    shutdown_at_time.sh <hours> <minutes> 
# 
# to enable shutdown mechanism.
#
#    shutdown_at_time.sh --off  
#
# to disable.
#
# We'll suppose the user only wants to have regular shutdown once a day
# as specified by the <hours> and <minutes> parameters. Thus, any line in
# crontab already specifying a shutdown will be deleted before a new one is
# inserted.

TCRON=/tmp/oldcron
USERCRON=/tmp/usercron
MESSAGE="Denne computer lukker ned om fem minutter"

crontab -l > $TCRON
sudo -u user crontab -l > $USERCRON


if [ "$1" == "--off" ]
then

    if [ -f $TCRON ]
    then
        sed -i -e "/\/sbin\/shutdown/d" $TCRON
        crontab $TCRON
    fi

    if [ -f $USERCRON ]
    then
        sed -i -e "/${MESSAGE}/d" $USERCRON
        crontab $USERCRON
    fi

else

    if [ $# == 2 ]
    then
        HOURS=$1
        MINUTES=$2
        # We still remove shutdown lines, if any
        if [ -f $TCRON ]
        then
            sed -i -e "/\/sbin\/shutdown/d" $TCRON
        fi
        if [ -f $USERCRON ]
        then
            sed -i -e "/${MESSAGE}/d" $USERCRON
        fi
        # Assume the parameters are already validated as integers.
        echo "$(expr $(expr $MINUTES + 5) % 60) $HOURS * * * /usr/sbin/shutdown now" >> $TCRON
        crontab $TCRON

        # Now output to user's crontab as well
        echo "$MINUTES $HOURS * * * DISPLAY=:0.0 /usr/bin/notify-send \"$MESSAGE\"" >> $USERCRON
        sudo -u user crontab $USERCRON
    else
        echo "Usage: shutdown_at_time.sh [--off] [hours minutes]"
    fi

fi

if [ -f $TCRON ]
then
    rm $TCRON
fi


     


