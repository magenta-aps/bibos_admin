#!/usr/bin/env bash

# Remove xscreensaver and reinstate Gnome screensaver.

apt-get remove xscreensaver xscreensaver-data-extra xscreensaver-gl-extra
apt-get install gnome-screensaver

rm -f /home/.skjult/.config/autostart/xscreensaver.desktop

# It's possible to remove local xscreensaver settings, but we let them be for
# now - maybe people would like to reinstate the screensaver and keep the old
# settings without having to remember them.
# 
# Uncomment the following line if you actually want to remove the settings
# when disabling the screensaver.

# rm -f /home/.skjult/.xscreensaver

exit 0
