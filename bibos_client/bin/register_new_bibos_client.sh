#!/usr/bin/env bash

    # Get hold of config parameters, connect to admin system.

    # Attempt to get shared config file from gateway.
    # It this fails, the user must enter the corresponding data (site and 
    # admin_url) manually.
    if [ "$(id -u)" != "0" ]
    then
        echo "Dette program skal køres som root." 1>&2
        exit 1
    fi
    
    echo "Indtast gateway, tryk <ENTER> for ingen gateway eller automatisk opsætning"
    read GATEWAY_IP

    if [[ -z $GATEWAY_IP ]]
    then
        # No gateway entered by user
        GATEWAY_SITE="http://$(bibos_find_gateway 2> /dev/null)" 
    else
        # User entered IP address or hostname - test if reachable by ping
        echo "Checker forbindelsen til gateway ..."
        ping -c 1 $GATEWAY_IP 2>1 > /dev/null
        if [[ $? -ne 0 ]]
        then
            echo "Ugyldig gateway-adresse ($GATEWAY_IP) - prøv igen."
            exit -1
        else
            echo "OK"
        fi
        # Gateway is pingable - we assume that means it's OK.
        GATEWAY_SITE="http://$GATEWAY_IP"
        set_bibos_config gateway "$GATEWAY_IP"
    fi

    SHARED_CONFIG="/tmp/bibos.conf"
    curl -s "$GATEWAY_SITE/bibos.conf" -o "$SHARED_CONFIG"

    if [[ -f "$SHARED_CONFIG" ]]
    then
        HAS_GATEWAY=1
    fi
    # The following config parameters are needed to finalize the
    # installation:
    # - hostname
    #   Prompt user for new host name
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
    if [[ -n "$HAS_GATEWAY" ]]
    then
        SITE=$(get_bibos_config site "$SHARED_CONFIG")
    fi
    
    if [[ -z "$SITE" ]]
    then 
        echo "Indtast ID for det site, computeren skal tilmeldes:"
        read SITE
    fi

    if [[ -n "$SITE" ]]
    then
        sudo set_bibos_config site $SITE
    else
        echo ""
        echo "Computeren kan ikke registreres uden site - prøv igen."
        exit 1
    fi


    # - distribution
    # Detect OS version and prompt user for verification	

    DISTRO=""
    if [[ -r /etc/os-release ]]; then
    	. /etc/os-release
        if [[ "$ID" = ubuntu ]]; then
		if [[ "$VERSION_ID" = "14.04" ]]; then
			DISTRO="BIBOS14.04" 
		elif [[ "$VERSION_ID" = "12.04" ]]; then
			DISTRO="BIBOS12.04"
		elif [[ "$VERSION_ID" = "16.04" ]]; then
			DISTRO="BIBOS16.04"
		else
			echo "Ubuntu versionen er ikke understøttet af BibOS systemet. Du kan alligevel godt forsøge at tilmelde PC'en til admin systemet."
			echo "Indtast ID for PC'ens distribution:"
			read DISTRO
		fi
        else
		echo "Dette er ikke en Ubuntu maskine. BibOS systemet understøtter kun Ubuntu. Du kan alligevel godt forsøge at tilmelde PC'en til admin systemet."	
		echo "Indtast ID for PC'ens distribution:"
	        read DISTRO
	fi
    else
    	echo "Vi kan ikke se hvilket operativ system der er installeret."
        echo "Indtast venligst ID for PC'ens distribution:"
        read DISTRO
    fi

    if [[ -z $DISTRO ]]
    then
        echo "Indtast ID for PC'ens distribution"
        read DISTRO
    fi

    echo "Distributions ID: "$DISTRO

    sudo set_bibos_config distribution $DISTRO


    # - mac
    #   Get the mac-address
    sudo set_bibos_config mac `ip addr | grep link/ether | awk 'FNR==1{print $2}'`


    # - admin_url
    #   Get from gateway, otherwise prompt user.
    if [[ -n "$HAS_GATEWAY" ]]
    then
        ADMIN_URL=$(get_bibos_config admin_url "$SHARED_CONFIG")
    fi
    if [[ -z "$ADMIN_URL" ]]
    then 
        ADMIN_URL="https://bibos-admin.magenta-aps.dk"
        echo "Indtast admin-url hvis det ikke er $ADMIN_URL"
        read NEW_ADMIN_URL
        if [[ -n $NEW_ADMIN_URL ]]
        then
            ADMIN_URL=$NEW_ADMIN_URL
        fi
    fi
    sudo set_bibos_config admin_url $ADMIN_URL

    # OK, we got the config. 
    # Do the deed.
    sudo bibos_register_in_admin

    # Now setup cron job
    if [[ -f $(which jobmanager) ]]
    then
        sudo echo 'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin' > /etc/cron.d/bibos-jobmanager
        sudo echo "*/5 * * * * root $(which jobmanager)" >> /etc/cron.d/bibos-jobmanager
    fi
