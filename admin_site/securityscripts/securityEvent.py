#!/usr/bin/env python 

import os
import sys
import linecache
from datetime import datetime

bufsize = 8192

numberOflines = 10
fname = "/var/log/syslog"
fsize = os.stat(fname).st_size
lines=""

syslog_iter = 0
with open(fname) as f:
    if bufsize > fsize:
        bufsize = fsize-1
    data = []
    while True:
        syslog_iter +=1
        f.seek(fsize-bufsize*syslog_iter)
        data.extend(f.readlines())
        if len(data) >= numberOflines or f.tell() == 0:
            lines += str(''.join(data[-numberOflines:]))
            break

securityEventFile = open("/etc/bibos/security/event.txt", "a")
securityEventFile.write("Timestamp: " + datetime.now().strftime('%Y%m%d%H%M') + "\n")
#Ignore first argument
iterargs = iter(sys.argv)
next(iterargs)
for arg in iterargs:    
        #find keyword
        #select text from keyword until end of line        
        before_keyword, keyword, after_keyword = lines.partition(arg)        
        if(after_keyword != ""):
            splittet_lines = after_keyword.splitlines()
            if(len(splittet_lines) > 0):
                securityEventFile.write(arg)        
                securityEventFile.write(splittet_lines[0]+"\n")

securityEventFile.write(lines+"\n")    
securityEventFile.close()