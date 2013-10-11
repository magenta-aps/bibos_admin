#!/usr/bin/env bash

# Disable Gnome screensaver, install A LOT of graphic screensavers,
# enable screensaver for user by default.


apt-get -y remove gnome-screensaver
apt-get -y install xscreensaver xscreensaver-data xscreensaver-gl

mkdir -p /home/.skjult/.config/autostart

cat << EOF > /home/.skjult/.config/autostart/xscreensaver.desktop

[Desktop Entry]
Type=Application
Exec=xscreensaver -nosplash
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name[da_DK]=Pauseskærm
Name=Pauseskærm
Comment[da_DK]=
Comment=
EOF

exit 0

