#!/usr/bin/env bash

username=$1
email=$2
domain=$3
port=$4

project_dir=$(dirname `pwd`)
admin_dir=$project_dir/bibos_admin
managepy="python $project_dir/manage.py"
managepy_cmds=( 
"makemigrations"
"migrate"
"createsuperuser --username $username --email $email"
"migrate --run-syncdb"
)


source $project_dir/python-env/bin/activate
for commands in "${managepy_cmds[@]}"
do
    $managepy $commands
done

cd $admin_dir
sed -i '/ALLOWED_HOSTS/ s/\[.*]/['"'$domain']"'/' settings_development.py
ln -s settings_development.py settings.py

printf "\n\n######\n\nhttp://$domain:$port/admin\n\n#####\n\n\n"
$managepy runserver 0:$port
