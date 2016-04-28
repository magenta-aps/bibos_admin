#!/usr/bin/env python
import os
import sys 
from datetime import datetime
#Dont give timestamp as argument 
#csv format: TimeStamp, securityEventCode, Name, PC, Tec sum, Raw data
#Ignore first argument

if(len(sys.argv) == 1):
    sys.exit()

line = datetime.now().strftime('%Y%m%d%H%M')
    
with open('securityevent.csv', 'a') as csvfile:
    for i in range(1, len(sys.argv)):      
        line += ',' + sys.argv[i]
    csvfile.write(line + '\n')