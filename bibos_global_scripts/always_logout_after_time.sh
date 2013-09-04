#!/usr/bin/env bash
# Logout the user from the graphical user interface after N minutes.
# Takes exactly one parameter.

if [ $# -ne 1 ]
then
    echo "This job takes exactly one parameter."
    exit -1
fi

if [[ ($1 == "--disable") || ($1 == "0") ]]
then
    # Clean up
    rm -f /usr/share/bibos/bin/auto_logout.sh
    rm -f /home/.skjult/.config/autostart/auto_logout.sh.desktop
    QUEUED_JOBS=$(atq)
    if [[ $QUEUED_JOBS ]]
    then
        atrm $(atq | awk '{ print $1; }')
    fi
    exit 0

fi

cat << EOF > /usr/share/bibos/bin/auto_logout.sh
#!/usr/bin/env bash

atrm \$(atq | awk '{ print \$1; } ')

TIME=$1

if [ \$TIME -ge 5 ]
then
    TM5=\$(expr \$TIME - 5)
    echo 'DISPLAY=:0.0 XAUTHORITY=/home/user/.Xauthority /usr/bin/zenity --warning --text="Du vil blive logget ud om fem minutter"' > /tmp/notify
     at -f /tmp/notify now + \$TM5 min 
fi

echo 'kill -9 -1' > /tmp/quit

at -f /tmp/quit now + \$TIME min

exit 0

EOF

chmod +x /usr/share/bibos/bin/auto_logout.sh

mkdir -p /home/.skjult/.config/autostart

cat << EOF > /home/.skjult/.config/autostart/auto_logout.sh.desktop

[Desktop Entry]
Type=Application
Exec=/usr/share/bibos/bin/auto_logout.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name[da_DK]=Autologud
Name=Autologud
Comment[da_DK]=
Comment=
EOF

chmod +x /home/.skjult/.config/autostart/auto_logout.sh.desktop

exit 0


