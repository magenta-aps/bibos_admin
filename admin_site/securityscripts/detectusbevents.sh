#!/bin/bash
echo "USB Keyboard attachment is detected." >> /var/log/usbevent.log

tail /var/log/syslog >> /var/log/usbevent.log
