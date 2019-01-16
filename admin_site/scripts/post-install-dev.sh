#!/usr/bin/env bash


if [ $# -lt 4 ] || [ $# -gt 4 ]
then
    printf "The command is used like this:\n\n    $0 USERNAME EMAIL DOMAIN/IP PORT\n\n"
else
    username=$1
    email=$2
    domain=$3
    port=$4
    timezone=`cat /etc/timezone`
    language=`echo "${LANG%%.*}"`
    secret_key=`openssl rand -base64 34 | head -c 50`

    project_dir=$(dirname "$0")/..
    admin_dir=$project_dir/bibos_admin
    managepy="python manage.py"
    managepy_cmds=( 
        "makemigrations"
        "migrate"
        "createsuperuser --username $username --email $email"
        "migrate --run-syncdb"
    )

cat <<ENV > $admin_dir/.env
# Django
ALLOWED_HOSTS = ['$domain']
DEBUG = True
SECRET_KEY = '$secret_key'
ADMINS = ('$username', '$email')

# Database
DB_ENGINE = 'django.db.backends.sqlite3'
DB_NAME = '.database.db'
DB_USER = ''
DB_PASSWORD = ''

# Email
DEFAULT_FROM_EMAIL = ''
ADMIN_EMAIL = ''
EMAIL_HOST = ''
EMAIL_PORT =

# Timezone/Language
TIME_ZONE = '$timezone'
LANGUAGE_CODE = '$language'

# Proxy
DEFAULT_ALLOWED_PROXY_HOSTS = []
DEFAULT_DIRECT_PROXY_HOSTS = []

CLOSED_DISTRIBUTIONS = ['BIBOS', 'BIBOS14.04', 'BIBOS16.04']
ENV

    cd $project_dir
    source ../python-env/bin/activate
    for commands in "${managepy_cmds[@]}"
    do
        $managepy $commands
    done

    printf "\n\n######\n\nhttp://$domain:$port/admin\n\n#####\n\n\n"
    $managepy runserver 0:$port
fi
