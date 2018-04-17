#!/usr/bin/env bash

username=$1
email=$2
domain=$3
port=$4

project_dir=$(dirname `pwd`)
admin_dir=$project_dir/bibos_admin
managepy="python $project_dir/manage.py"
user="createsuperuser --username $username --email $email"
commands=( "makemigrations" "migrate" $user "migrate --run-syncdb")

$admin_dir/settings_development.py | sed '/ALLOWED_HOSTS/ s/\[.*]/['"'$domain']"'/'
ln -s $admin_dir/settings_development.py $admin_dir/settings.py

for command in "${commands[@]}"
do
    $managepy $command
done

printf "\n\n######\n\nhttp://$domain:$port/admin\n\n#####\n\n\n"
$managepy runserver 0:$port
