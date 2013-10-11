#!/bin/bash

# BIBOS_SCRIPT_TITLE: Afinstaller pakker
#
# Tager eet argument, en kommasepareret liste af pakker, der skal afinstalleres:
#
# BIBOS_SCRIPT_ARG:STRING
#

apt-get -y remove `echo $1 | tr ",", " "`
