#!/usr/bin/env bash

# Setup virtualenv, install packages necessary to run BibOS Admin.
# System requirements, installed packages etc. should be checked 
# in a separate Dependencies script which should be combined with this one.

virtualenv .
source bin/activate
pip install django
pip install pep8==1.2


