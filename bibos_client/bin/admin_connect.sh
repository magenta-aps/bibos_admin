#!/bin/bash

# Remember to increase the version number if any changes are made!
VERSION=1.0

sudo apt-get update
sudo apt-get upgrade --assume-yes
sudo apt-get install curl --assume-yes
sudo apt-get install python-dev --assume-yes
sudo apt-get install python-pip --assume-yes
sudo pip uninstall netifaces -y
sudo pip install lockfile
sudo pip install --upgrade bibos-client
sudo mkdir -p /var/lib/bibos/jobs/
sudo mkdir -p /etc/bibos/security/
sudo set_bibos_config admin_connect_version $VERSION
sudo register_new_bibos_client.sh
