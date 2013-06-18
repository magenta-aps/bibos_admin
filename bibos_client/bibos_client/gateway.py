import sys
import re
import socket
import commands
from socket import AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST

MESSAGE = "Hello"
REPLY_MESSAGE = "BibOS-server:"
PORT = 42420


def find_lan_addresses():
    get_ip = False
    for line in commands.getoutput("/sbin/ifconfig").split("\n"):
        if re.match('^\s*eth\d+\s+', line):
            get_ip = True
        else:
            if get_ip:
                m = re.search('addr:(\d+.\d+.\d+.\d+)\s*' +
                              'Bcast:(\d+.\d+.\d+.\d+)',
                              line)
                if m is not None:
                    return (m.group(1), m.group(2))
                get_ip = False
    return (None, None)


def find_gateway():
    lan_ip = None
    broadcast_addr = None

    (lan_ip, broadcast_addr) = find_lan_addresses()

    if not broadcast_addr:
        sys.stderr.write("Could not find broadcast address")
        sys.exit(1)

    try:
        sock = socket.socket(AF_INET, SOCK_DGRAM)  # UDP
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
        sys.stderr.write("Exception: " + str(inst) + "\n")
        return None

if(__name__ == '__main__'):
    s = find_gateway()
    if s is not None:
        print s
