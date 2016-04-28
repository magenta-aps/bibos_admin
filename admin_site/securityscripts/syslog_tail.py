import os
import sys
import linecache

def get_syslog_tail(numberOflines):
    bufsize = 8192
    
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
            
    return lines