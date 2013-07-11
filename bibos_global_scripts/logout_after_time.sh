#!/usr/bin/env bash
# Logout the user from the graphical user interface after N minutes.
# Takes exactly one parameter.

if [ $# -ne 1 ]
then
    echo "This job takes exactly one parameter."
    exit -1
fi

TIME=$1

if [ $TIME -ge 5 ]
then
    TM5=$(expr $TIME - 5)
    echo 'DISPLAY=:0.0 XAUTHORITY=/home/user/.Xauthority /usr/bin/zenity --warning --text="Computeren lukkes ned om fem minutter"' > /tmp/notify
     at -f /tmp/notify now + $TM5 min 
fi

echo '/sbin/reboot' > /tmp/quit

at -f /tmp/quit now + $TIME min

exit 0


