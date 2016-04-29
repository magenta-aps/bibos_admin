#!/usr/bin/env bash

sudo cp 91-detectusbevents.rules /etc/udev/rules.d
sudo mkdir /etc/bibos/security
sudo cp csv_writer.py syslog_tail.py keyboardEvent.py /etc/bibos/security
sudo chmod gu+x /etc/bibos/security/keyboardEvent.py

