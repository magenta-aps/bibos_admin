#!/usr/bin/env bash


bin_folder="/usr/local/bin"
copy_cmd="sudo cp -v"

$copy_cmd ../bibos_client/admin_client.py /usr/local/lib/python2.7/dist-packages/bibos_client
$copy_cmd bibos_register_in_admin $bin_folder
$copy_cmd register_new_bibos_client.sh $bin_folder
