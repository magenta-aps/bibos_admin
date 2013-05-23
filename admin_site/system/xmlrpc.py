# This module contains the implementation of the XML-RPC API used by the
# client.

from models import PC, Site, Distribution, Configuration, ConfigurationEntry


def register_new_computer(name, uid, distribution, site, configuration):
    """Register a new computer with the admin system - after registration, the
    computer will be submitted for approval."""

    new_pc = PC.objects.get(uid=uid)

    if not new_pc:
        new_pc = PC()
        # Assume PCs are never reused on another site
        new_pc.site = Site.objects.get(uid=site)  
    new_pc.name = name
    new_pc.uid = uid
    
    new_pc.distribution = Distribution.objects.get(uid=distribution)  
    new_pc.is_active = False
    # Create new configuration, populate with data from computer's config.
    # If a configuration with the same ID is hanging, reuse.
    config_name = '_'.join([site, name, uid])
    my_config = Configuration.objects.get(name=config_name)
    if not my_config:
        my_config = Configuration()
        my_config.name = config_name
    else:
        # Delete pre-existing entries
        entries = ConfigurationEntry.objects.filter(
            owner_configuration=my_config)
        for e in entries:
            e.delete()
    my_config.save()
    # And load configuration
    for k, v in configuration.items():
        entry = ConfigurationEntry(key=k, value=v,
                                   owner_configuration=my_config)
        entry.save()
    # Set and save PC.
    new_pc.configuration = my_config
    new_pc.save()
    return 0


def send_status_info(pc_uid, package_data, job_data):
    """Update package lists as well as the status of outstanding jobs.
    If no updates of package or job data, these will be None. In that
    case, this function really works as an "I'm alive" signal."""

    # TODO: Code this

    # 1. Lookup PC, update "last_see" field
    # 2. Update package lists with package data
    # 3. Update jobs with job data

    return 0


def get_instructions(pc_uid):
    """This function will ask for new instructions in the form of a list of
    jobs, which will be scheduled for execution and executed upon receipt.
    These jobs will generally take the form of bash scripts."""

    jobs = []

    # TODO: Retrieve non-submitted jobs, mark them as subitted and send to the
    # client denoted by UID.

    return jobs
