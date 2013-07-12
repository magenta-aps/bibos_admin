#!/usr/bin/env python
"""This file contains utilities for communicating with the BibOS admin
system."""

import hashlib
import uuid
import netifaces
import os
import sys
import csv
import urlparse
import re
import subprocess

from bibos_utils.bibos_config import BibOSConfig
from bibos_client.admin_client import BibOSAdmin


def get_upgrade_packages():
    matcher = re.compile('Inst\s+(\S+)')
    prg = subprocess.Popen(
        ['apt-get', '--just-print',  'dist-upgrade'],
        stdout=subprocess.PIPE
    )
    result = []
    for line in prg.stdout.readlines():
        m = matcher.match(line)
        if m:
            result.append(m.group(1))
    return result


def upload_packages():
    config = BibOSConfig()
    data = config.get_data()

    admin_url = data['admin_url']
    xml_rpc_url = data.get('xml_rpc_url', '/admin-xml/')
    uid = data['uid']

    admin = BibOSAdmin(urlparse.urljoin(admin_url, xml_rpc_url))

    # TODO: Make option to turn off/avoid repeating this.
    os.system('get_package_data /tmp/packages.csv')

    upgrade_pkgs = set(get_upgrade_packages())

    with open('/tmp/packages.csv') as f:
        package_reader = csv.reader(f, delimiter=';')
        package_data = [
            {
                'name': n,
                'status': 'needs upgrade' if n in upgrade_pkgs else s,
                'version': v,
                'description': d
            } for (n, s, v, d) in package_reader
        ]

    try:
        admin.send_status_info(uid, package_data, None)
    except Exception as e:
        print >> sys.stderr, 'Error:', str(e)
        sys.exit(1)


def upload_dist_packages():
    config = BibOSConfig()
    data = config.get_data()

    admin_url = data['admin_url']
    xml_rpc_url = data.get('xml_rpc_url', '/admin-xml/')
    distribution = data['distribution']

    admin = BibOSAdmin(urlparse.urljoin(admin_url, xml_rpc_url))

    # TODO: Make option to turn off/avoid repeating this.
    os.system('get_package_data /tmp/packages.csv')

    with open('/tmp/packages.csv') as f:
        package_reader = csv.reader(f, delimiter=';')
        package_data = [
            {'name': n, 'status': s, 'version': v, 'description': d} for
            (n, s, v, d) in package_reader]

    try:
        admin.upload_dist_packages(distribution, package_data)
    except Exception as e:
        print >> sys.stderr, 'Error:', str(e)
        sys.exit(1)
