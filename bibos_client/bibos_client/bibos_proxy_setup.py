# This script is meant to be called with a simple
# "import bibos_client.bibos_proxy_setup" and will automatically configure
# the neccessary proxy environment variables to use a BibOS gateway proxy.

import os
from bibos_client.gateway import find_gateway

if 'http_proxy' not in os.environ:
    gw = find_gateway(timeout=1)
    if gw is not None:
        proxy_url = "http://%s:8000" % gw
        os.environ['http_proxy'] = proxy_url
        os.environ['https_proxy'] = proxy_url
        os.environ['ftp_proxy'] = proxy_url
