#!/usr/bin/env bash


git_url=https://raw.githubusercontent.com/magenta-aps/bibos_admin/feature/22059-update/bibos_client
bin_folder="/usr/local/bin"

sudo curl $git_url/bibos_client/admin_client.py > /usr/local/lib/python2.7/dist-packages/bibos_client/admin_client.py
sudo curl $git_url/bin/bibos_register_in_admin > $bin_folder/bibos_register_in_admin
sudo curl $git_url/bin/register_new_bibos_client.sh > $bin_folder/register_new_bibos_client.sh
