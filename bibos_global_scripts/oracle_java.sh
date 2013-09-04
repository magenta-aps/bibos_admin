#!/usr/bin/env bash
# NOTE: This script requires access to keys.gnupg.org.
# In order for this to work through a gateway, that server MUST
# be enabled in proxy settings.

echo "deb http://www.duinsoft.nl/pkg debs all" > /tmp/oracle_java.list
mv /tmp/oracle_java.list /etc/apt/sources.list.d
apt-key adv --keyserver keys.gnupg.net --recv-keys 5CB26B26
apt-get -y update
set -e
apt-get -y --force-yes install update-sun-jre

exit 0

