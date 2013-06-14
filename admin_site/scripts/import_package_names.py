#!/usr/bin/env python

import os
import os.path
import sys
import urllib2
import gzip
import re

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))

from bibos_admin import settings
from system.models import Package

def import_packages(url):
    f = urllib2.urlopen(url)
    fh = open('/tmp/bibos_import_packages.gz', 'w+');
    fh.write(f.read())
    fh.close()
    fh = gzip.open('/tmp/bibos_import_packages.gz')
    matcher = re.compile('(\S+)\s+\(([^\)]+)\)\s+(\[[^\]]+\]\s+)?([^\n]+)')
    for line in fh:
        m = matcher.match(line)
        if m is not None:
            try:
                Package.objects.get(name=m.group(1), version=m.group(2))
            except Package.DoesNotExist:
                p = Package(
                    name=m.group(1),
                    version=m.group(2),
                    description=m.group(4)
                )
                print "Creating %s (%s)" % (m.group(1), m.group(2))
                p.save()
    

def usage():
    usage = """
Usage:
  %s <url>

  The file at the URL should be in the format used by
  http://packages.ubuntu.com/precise/allpackages?format=txt.gz

"""
    print >>os.sys.stderr, usage % __file__

if __name__ == '__main__':
    if len(sys.argv) == 2:
        import_packages(sys.argv[1])
    else:
        usage()
