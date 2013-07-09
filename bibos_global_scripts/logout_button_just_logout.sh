#!/usr/bin/env bash

# This script is Aarhus specific. It places a Logout button on the audience
# user's desktop which will also log out from the Internet.
# 
# It replaces the old "Log out from the Internet" button.
#
# After the script is run, the audience user must log out and log in again for
# it to take effekt.

cat << EOF > /home/.skjult/Desktop/Logout.desktop

[Desktop Entry]
Version=1.0
Type=Application
Name=Log ud
Comment=Logout-funktion til bibliotekerne i Aarhus
Icon=application-exit
Exec=gnome-session-quit

EOF

exit 0
