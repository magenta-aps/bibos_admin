from django.template import Context, loader as template_loader
from random import sample, choice
from bibos_admin import settings
from models import PC, ConfigurationEntry

import string
import os
import subprocess


def make_proxy_password(pc):
    # Generate a password
    chars = string.letters + string.digits
    length = 8
    proxy_password = ''.join([choice(chars) for i in range(length)])
    ConfigurationEntry.objects.create(
        key='proxy_upstream_password',
        value=proxy_password,
        owner_configuration=pc.configuration
    )

    # Update htpasswd file
    cmd = ['/usr/bin/htpasswd', '-b']
    if not os.path.isfile(settings.PROXY_HTPASSWD_FILE):
        cmd.append('-c')
    cmd.extend([
        settings.PROXY_HTPASSWD_FILE,
        pc.uid,
        proxy_password
    ])
    subprocess.call(cmd)

    return proxy_password


def get_proxy_setup(pc_uid):
    pc = PC.objects.get(uid=pc_uid)

    # Check if we have a password, otherwise generate one
    try:
        entry = pc.configuration.entries.get(
            key='proxy_upstream_password'
        )
        proxy_password = entry.value
    except ConfigurationEntry.DoesNotExist:
        proxy_password = make_proxy_password(pc)

    context = Context({
        'allowed_hosts': pc.get_merged_config_list(
            'proxy_allowed_hosts',
            default=settings.DEFAULT_ALLOWED_PROXY_HOSTS
        ),
        'upstream_host': pc.get_config_value(
            'proxy_upstream_host',
            'bibos-proxy.web06.magenta-aps.dk'
        ),
        'upstream_port': pc.get_config_value(
            'proxy_upstream_port',
            '80'
        ),
        'login': pc.uid,
        'password': proxy_password
    })

    direct_hosts_str = pc.get_config_value('proxy_direct_hosts')
    if direct_hosts_str:
        if direct_hosts_str != '':
            context['direct_hosts'] = [
                s.strip() for s in direct_hosts_str.split(",")
            ]
    else:
        context['direct_hosts'] = settings.DEFAULT_DIRECT_PROXY_HOSTS

    template = template_loader.get_template(
        'proxyconf/squid-deb-proxy.conf'
    )

    return str(template.render(context))
