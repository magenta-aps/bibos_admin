#project_root="`pwd`/../"

#settings_development.py | sed '/ALLOWED_HOSTS/ s/\[.*]/['"'$4']"'/'
#ln -s $project_root/bibos_admin/settings_development.py $project_root/bibos_admin/settings.py

managepy="python $project_root/manage.py"
user="createsuperuser --username $1 --password $2 --email $3"
commands=( "makemigrations" "migrate" "$user" "migrate --run-syncdb")

for command in "${commands[@]}"
do
    $managepy $command
done

printf "\n\n######\n\nhttp://$4:$5/admin\n\n#####\n\n\n"
echo "$managepy runserver 0:$5"
