#!/usr/bin/env bash


if [ $# -lt 4 ] || [ $# -gt 4 ]
then
    printf "The command is used like this:\n\n    post-install-dev.sh USERNAME EMAIL DOMAIN/IP PORT\n\n"
else
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

    cd $admin_dir
    sed -i '/ALLOWED_HOSTS/ s/\[.*]/['"'$domain']"'/' settings_development.py
    ln -s settings_development.py settings.py

    source $project_dir/python-env/bin/activate
    for commands in "${managepy_cmds[@]}"
    do
        $managepy $commands
    done

    printf "\n\n######\n\nhttp://$domain:$port/admin\n\n#####\n\n\n"
    $managepy runserver 0:$port
fi
