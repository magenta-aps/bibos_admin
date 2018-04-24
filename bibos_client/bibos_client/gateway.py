import os
import re
import socket
import netifaces
from socket import AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST

from bibos_utils import bibos_config

MESSAGE = "Hello"
REPLY_MESSAGE = "BibOS-server:"
PORT = 42420


def find_gateway(timeout=1):
    result = None

    if bibos_config.has_config('gateway'):
        # Done
        ip = bibos_config.get_config('gateway')
        rc = os.system("ping -c 1 " + ip + " 2>&1 > /dev/null")
        if rc == 0:
            result = ip
        return result

    for if_name in netifaces.interfaces():
        if if_name.startswith('eth'):
            interface = netifaces.ifaddresses(if_name)
            if netifaces.AF_INET in interface:
                broadcast_addr = interface[netifaces.AF_INET][0]['broadcast']
            else:
                continue
            # Now we know this IF is plugged in.
            try:
                sock = socket.socket(AF_INET, SOCK_DGRAM)
                sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
                sock.sendto(MESSAGE, (broadcast_addr, PORT))
                sock.settimeout(timeout)
                data, addr = sock.recvfrom(1024)
                m = re.match("^" + REPLY_MESSAGE + "(.+)", data)
                if m is not None:
                    result = m.group(1)
            except Exception:
                # sys.stderr.write("Exception: " + str(inst) + "\n")
                return None
        if result is not None:
            break

    return result

if(__name__ == '__main__'):
    s = find_gateway()
    if s is not None:
        print s
