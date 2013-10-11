#!/bin/bash

# BIBOS_SCRIPT_TITLE: Installer eller opgrader pakker
#
# Tager eet argument, en kommasepareret liste af pakker, der skal
# installeres/opgraderes:
#
# BIBOS_SCRIPT_ARG:STRING
#

apt-get -y install `echo $1 | tr ",", " "`
