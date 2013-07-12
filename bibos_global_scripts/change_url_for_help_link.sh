#!/usr/bin/env bash

# Change the URL of the Help icon on the audience user's desktop.
# If there is no Help icon, it is created.

HELP_URL="https://help.ubuntu.com"

if [ $# -ge 1 ]
then
    HELP_URL=$1
    # Don't care if people supply too many parameters.
fi

cat << EOF > /home/.skjult/Desktop/Help.desktop

[Desktop Entry]
Version=1.0
Type=Link
Name=Hjælp
Comment=Logout-funktion til bibliotekerne i Aarhus
Icon=help
URL=$HELP_URL

EOF

exit 0

