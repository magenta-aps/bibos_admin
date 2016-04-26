#!/usr/bin/env python 

import os
import sys
import linecache
from datetime import datetime

syslog = "/var/log/syslog"
totalNumberOfLines = len(open(syslog).readlines())

lines=""
# use line cache module to read the lines
for i in range(totalNumberOfLines - 10 + 1, totalNumberOfLines+1):
     lines += str(linecache.getline(syslog,i),)

securityEventFile = open("/etc/bibos/security/event.txt", "a")
securityEventFile.write("Timestamp: " + datetime.now().strftime('%Y%m%d%H%M') + "\n")
#Ignore first argument
iterargs = iter(sys.argv)
next(iterargs)
for arg in iterargs:    
        #find keyword
        #select text from keyword until end of line        
        before_keyword, keyword, after_keyword = lines.partition(arg)
        securityEventFile.write(arg)
        if(after_keyword != ""):
            splittet_lines = after_keyword.splitlines()
            if(len(splittet_lines) > 0):        
                securityEventFile.write(splittet_lines[0]+"\n")

securityEventFile.write(lines+"\n")    
securityEventFile.close()