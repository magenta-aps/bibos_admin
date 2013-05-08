import sys, time, re
from socket import *
import commands

PORT = 42420
MESSAGE = "Hello"
REPLY_MESSAGE = "BibOS-server:"

# TODO:
#  Use config instead of discovery
#  Make it possible to get full server-config from the local server

def find_lan_addresses():
    get_ip = False
    for line in commands.getoutput("/sbin/ifconfig").split("\n"):
        if re.match('^\s*eth\d+\s+', line):
            get_ip = True
        else:
            if get_ip:
                m = re.search('addr:(\d+.\d+.\d+.\d+)\s*' +
                              'Bcast:(\d+.\d+.\d+.\d+)',
                              line);
                if m is not None:
                    return (m.group(1), m.group(2))
                get_ip = False
    return (None, None)

def run_server(args=[]):
    server_ip = None
    
    if(len(args) > 0):
        server_ip = args[0]
    else:
        server_ip = find_lan_addresses()[0]
    
    if not server_ip:
        sys.stderr.write("Could not find LAN ip or no LAN ip specified\n")
        sys.exit(1)

    print "Running server, will reply with address", server_ip

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('', PORT))
    
    while 1:
        data, addr = sock.recvfrom(1024)
        print "Got", data, "from", addr
        sock.sendto(REPLY_MESSAGE + server_ip, addr)

def find_local_server(args=[]):
    lan_ip = None
    broadcast_addr = None
    
    if len(args) > 0:
        lan_ip = args[0]
        broadcast_addr = re.replace(".\d+$", lan_ip)
    else:
        (lan_ip, broadcast_addr) = find_lan_addresses()
    
    if not broadcast_addr:
        sys.stderr.write("Could not find broadcast address and " +
                         "address not specified\n")
        sys.exit(1)

    try:
        sock = socket(AF_INET, # Internet
                      SOCK_DGRAM) # UDP
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        sock.sendto(MESSAGE, (broadcast_addr, PORT))
        sock.settimeout(5)
        data, addr = sock.recvfrom(1024)
        m = re.match("^" + REPLY_MESSAGE + "(.+)", data)
        if m is not None:
            return m.group(1)
        else:
            return None
    except Exception as inst:
        print "Exception: ", inst 
        return None

if __name__ == '__main__':
    script = sys.argv.pop(0)
    if len(sys.argv) > 0:
        arg = sys.argv.pop(0)

        # If first argument is 'client', run the client
        if arg == 'findserver':
            result = find_local_server(sys.argv)
            if result is not None:
                print result
            sys.exit();

        # if first argument is 'server' remove it
        if arg == 'runserver':
            run_server(sys.argv)
            sys.exit();

    sys.stderr.write("Invalid arguments\n")
    sys.stderr.write(" Usage: " + script + " (runserver|findserver) " +
                     "[LAN_IP_ADDRESS]\n")
    sys.exit(1)
    

