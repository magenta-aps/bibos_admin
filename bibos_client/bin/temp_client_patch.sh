#!/usr/bin/env bash


bin_folder="/local/bin"

cp ../admin_client.py /usr/local/lib/python2.7/dist-packages/bibos_client
cp bibos_register_in_admin $bin_folder
cp register_new_bibos_client.sh $bin_folder
