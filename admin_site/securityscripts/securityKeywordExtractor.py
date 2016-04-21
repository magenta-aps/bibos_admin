#securityLogPath = "/var/log/"

def searchByKeywords(keywords):
    securityEventFile = open("securityEvent.txt", "w")
    file = open('aarhus.log', 'r')
    for keyword in keywords:    
        #find keyword
        #select text from keyword until end of line
        lines = file.read()
        befor_keyword, keyword, after_keyword = lines.partition(keyword)
        securityEventFile.write(after_keyword.splitlines()[0])
        
    securityEventFile.close()
