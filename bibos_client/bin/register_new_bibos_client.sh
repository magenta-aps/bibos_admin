#!/usr/bin/env bash

    # Get hold of config parameters, connect to admin system.
    # The following config parameters are needed to finalize the
    # installation:
    # - hostname
    #   TODO: Prompt user for new host name
    echo "Indtast venligst et nyt navn for denne computer:"
    read NEWHOSTNAME

    if [[ -n "$NEWHOSTNAME" ]]
    then
        echo $NEWHOSTNAME > /tmp/newhostname
        sudo cp /tmp/newhostname /etc/hostname
        sudo set_bibos_config hostname $NEWHOSTNAME
        sudo hostname $NEWHOSTNAME
        sudo sed -i -e "s/$HOSTNAME/$NEWHOSTNAME/" /etc/hosts
    else
        sudo set_bibos_config hostname $HOSTNAME
    fi
    # - site
    #   TODO: Get site from gateway, if none present prompt user
    echo "Indtast ID for det site, computeren skal tilmeldes:"
    read SITE
    if [[ -n "$SITE" ]]
    then
        sudo set_bibos_config site $SITE
    else
        echo ""
        echo "Computeren kan ikke registreres uden site - prøv igen."
        exit 1
    fi

    # - distribution
    #   TODO: Use preinstalled default if any, otherwise prompt user
    
    DISTRO=$(get_bibos_config distribution)
    echo $DISTRO

    if [[ -z $DISTRO ]]
    then
        echo "Indtast ID for PC'ens distribution"
        read DISTRO
    fi
    sudo set_bibos_config distribution $DISTRO
    # - admin_url
    #   TODO: Get from gateway, otherwise prompt user.
    ADMIN_URL=http://bibos-admin.magenta-aps.dk
    echo "Indtast admin-url hvis det ikke er $ADMIN_URL"
    read NEW_ADMIN_URL
    if [[ -n $NEW_ADMIN_URL ]]
    then
        ADMIN_URL=$NEW_ADMIN_URL
    fi
    sudo set_bibos_config admin_url $ADMIN_URL

    # OK, we got the config. 
    # Do the deed.
    sudo bibos_register_in_admin
