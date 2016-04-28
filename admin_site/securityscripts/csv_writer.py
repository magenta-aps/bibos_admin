#!/usr/bin/env python 
import os 
from datetime import datetime
#Dont give timestamp as argument 
#csv format: TimeStamp, securityEventCode, Name, PC, Tec sum, Raw data

def write_data(data):
    if(len(data) == 0):
        return
    
    line = datetime.now().strftime('%Y%m%d%H%M')
    for value in data:      
        line += ',' + value        
    
    csvfile = open("/etc/bibos/security/securityevent.csv", "a")
    csvfile.write(line + '\n')