#!/usr/bin/env python 

import os
import sys
import syslog_tail
import csv_writer
from datetime import datetime
from bibos_utils.bibos_config import BibOSConfig

#Get lines from syslog
lines = syslog_tail.get_syslog_tail(10)

#Ignore if not a keyboard event
if(lines.partition('keyboard')[2] == ""):
        sys.exit()

#securityEventCode, Name, PC, Tec sum, Raw data
csv_data = []
#securityEventCode
csv_data.append("KEYBOARD")
#Name
csv_data.append("Keyboard added")
#PC
csv_data.append(BibOSConfig().get_value("hostname"))

#Ignore first argument
for i in range(1, len(sys.argv)):
        #find keyword
        #select text from keyword until end of line        
        before_keyword, keyword, after_keyword = lines.partition(sys.argv[i])        
        if(after_keyword != ""):
            splittet_lines = after_keyword.splitlines()
            if(len(splittet_lines) > 0):
                #Tec sum
                csv_data.append("'" + splittet_lines[0] + "'")

lines = lines.replace('\n', ' ').replace('\r', '').replace(',','')

#Raw data
csv_data.append("'" + lines + "'")

csv_writer.write_data(csv_data)