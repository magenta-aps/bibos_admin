#!/bin/bash

#extract needed data.
#what is needed data???
#keywords : keyboard, Product, Manufacturer, input

echo "USB Keyboard attachment is detected." >> /var/log/usbevent.log

tail /var/log/syslog >> /var/log/usbevent.log

python securityKeywordExtractor.py ['Product:', 'Manufacturer:', 'input:']
