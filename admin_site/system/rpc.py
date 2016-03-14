# This module contains the implementation of the XML-RPC API used by the
# client.

import datetime
import system.proxyconf
from django.db.models import Q

from django.conf import settings

from models import PC, Site, Distribution, Configuration, ConfigurationEntry
from models import PackageList, Package, PackageStatus, CustomPackages
from job.models import Job, Script


def register_new_computer(name, uid, distribution, site, configuration):
    """Register a new computer with the admin system - after registration, the
    computer will be submitted for approval."""

    try:
        new_pc = PC.objects.get(uid=uid)
        package_list = new_pc.package_list
        custom_packages = new_pc.custom_packages
    except PC.DoesNotExist:
        new_pc = PC(name=name, uid=uid)
        new_pc.site = Site.objects.get(uid=site)
        # TODO: Better to enforce existence of package list in AfterSave
        # signal.
        package_list = PackageList(name=name)
        custom_packages = CustomPackages(name=name)

    new_pc.distribution = Distribution.objects.get(uid=distribution)
    new_pc.is_active = False
    # Create new configuration, populate with data from computer's config.
    # If a configuration with the same ID is hanging, reuse.
    config_name = '_'.join([site, name, uid])
    try:
        my_config = Configuration.objects.get(name=config_name)
    except Configuration.DoesNotExist:
        my_config = Configuration()
        my_config.name = config_name
    finally:
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
    # Tell us about yourself
    new_pc.do_send_package_info = True
    # Set and save PmC
    new_pc.configuration = my_config
    package_list.save()
    new_pc.package_list = package_list
    custom_packages.save()
    new_pc.custom_packages = custom_packages
    new_pc.save()
    return 0


def upload_dist_packages(distribution_uid, package_data):
    """This will upload the packages and package versions for a given
    BibOS distribution. A BibOS distribution is here defined as a completely
    fresh install of a standardized Debian-like system which is to be supported
    by the BibOS admin."""

    if distribution_uid in settings.CLOSED_DISTRIBUTIONS:
        # Ignore
        return 0

    distribution = Distribution.objects.get(uid=distribution_uid)

    if package_data is not None:
        distribution.package_list.packages.clear()

        for pd in package_data:
            # First, assume package & version already exists.
            try:
                p = Package.objects.get(name=pd['name'], version=pd['version'])
            except Package.DoesNotExist:
                p = Package.objects.create(
                    name=pd['name'],
                    version=pd['version'],
                    description=pd['description']
                )
            finally:
                status = PackageStatus.objects.create(
                    package=p,
                    package_list=distribution.package_list,
                    status=pd['status']
                )
    return 0


def send_status_info(pc_uid, package_data, job_data, update_required):
    """Update package lists as well as the status of outstanding jobs.
    If no updates of package or job data, these will be None. In that
    case, this function really works as an "I'm alive" signal."""

    # TODO: Code this

    # 1. Lookup PC, update "last_seen" field
    pc = PC.objects.get(uid=pc_uid)

    if not pc.is_active:
        # Fail silently
        return 0

    pc.last_seen = datetime.datetime.now()
    pc.save()

    # 2. Update package lists with package data
    if package_data and pc.do_send_package_info:
        # Ignore if we didn't ask for this

        # Clear existing packages
        pc.package_list.packages.clear()

        # Insert new ones
        # package_data is a list of dicts with the correct field names.
        for pd in package_data:
            # First, assume package & version already exists.
            try:
                p = Package.objects.get(name=pd['name'], version=pd['version'])
            except Package.DoesNotExist:
                p = Package.objects.create(
                    name=pd['name'],
                    version=pd['version'],
                    description=pd['description']
                )
            finally:
                status = PackageStatus.objects.create(
                    package=p,
                    package_list=pc.package_list,
                    status=pd['status']
                )
        # Assume no packages are any longer "pending".
        pc.custom_packages.update_by_package_names(pc.pending_packages_remove,
                                                   pc.pending_packages_add)
        # We just got the package info update we requested, so clear the flag
        # until we need a new update.
        pc.do_send_package_info = False

    # 3. Update jobs with job data
    if job_data is not None:
        for jd in job_data:
            job = Job.objects.get(pk=jd['id'])
            job.status = jd['status']
            job.started = jd['started']
            job.finished = jd['finished']
            job.log_output = jd['log_output']
            job.save()

    # 4. Check if update is required.
    if update_required is not None:
        updates, security_updates = map(int, update_required)
        if security_updates > 0:
            pc.is_update_required = True
            # See if things have changed and we need to update the package
            # lists.
            old_updates = int(pc.configuration.get('updates', 0))
            old_security = int(pc.configuration.get('security_updates', 0))
            if (security_updates > old_security) or (updates > old_updates):
                pc.do_send_package_info = True
            else:
                pc.do_send_package_info = False
        elif pc.is_update_required:
            pc.is_update_required = False
        # Save update info in configuration
        pc.configuration.update_entry('updates', updates)
        pc.configuration.update_entry('security_updates', security_updates)

    pc.save()

    return 0


def get_instructions(pc_uid, update_data):
    """This function will ask for new instructions in the form of a list of
    jobs, which will be scheduled for execution and executed upon receipt.
    These jobs will generally take the form of bash scripts."""

    pc = PC.objects.get(uid=pc_uid)

    pc.last_seen = datetime.datetime.now()
    pc.save()

    if not pc.is_active:
        # Fail silently
        return ([], False)

    update_pkgs = update_data.get('updated_packages', [])
    if len(update_pkgs) > 0:
        for pdata in update_pkgs:
            # Find or create the package in the global collection of packages
            try:
                p = Package.objects.get(
                    name=pdata['name'],
                    version=pdata['version']
                )
            except Package.DoesNotExist:
                p = Package(
                    name=pdata['name'],
                    version=pdata['version'],
                    description=pdata['description']
                )
                p.save()
            # Change or create the package status for the package/PC
            p_status = pc.package_list.statuses.filter(
                package__name=pdata['name'],
            ).delete()
            p_status = PackageStatus(
                status='install',
                package=p,
                package_list=pc.package_list
            )
            p_status.save()

            pc.package_list.statuses.filter(
                package__name=pdata['name'],
                package__version=pdata['version'],
            ).update(status='installed ok')

    remove_pkgs = update_data.get('removed_packages', [])
    if len(remove_pkgs) > 0:
        pc.package_list.statuses.filter(package__name__in=remove_pkgs).delete()

    # Get list of packages to install and remove.
    to_install, to_remove = pc.pending_package_updates

    # Add packages that are pending update to the list of packages we want
    # installed, as apt-get will upgrade any package in the package list
    # for apt-get install.
    for p in pc.package_list.pending_upgrade_packages:
        to_install.add(p.name)

    # Make sure packages added to be upgraded now are no longer pending.
    pc.package_list.flag_needs_upgrade(
        [p.name for p in pc.package_list.pending_upgrade_packages]
    )

    # Make sure packages we just installed are not flagged for removal
    for name in [p['name'] for p in update_pkgs]:
        if name in to_remove:
            pc.custom_packages.update_package_status(name, True)
            to_remove.remove(name)

    # Make sure packages we just removed are not flagged for installation
    for name in remove_pkgs:
        if name in to_install:
            pc.custom_packages.update_package_status(name, False)
            to_install.remove(name)

    if len(to_remove):
        sc = Script.get_system_script('remove_packages.sh')
        sc.run_on_pc(pc, ','.join(to_remove))

    if len(to_install):
        sc = Script.get_system_script('install_or_upgrade_packages.sh')
        sc.run_on_pc(pc, ','.join(to_install))

    jobs = []
    for job in pc.jobs.filter(status=Job.NEW):
        job.status = Job.SUBMITTED
        job.save()
        jobs.append(job.as_instruction)

    result = {
        'jobs': jobs,
        'configuration': pc.get_full_config(),
    }

    if pc.do_send_package_info:
        result['do_send_package_info'] = True

    return result


def get_proxy_setup(pc_uid):
    pc = PC.objects.get(uid=pc_uid)
    if not pc.is_active:
        return 0
    return system.proxyconf.get_proxy_setup(pc_uid)


def push_config_keys(pc_uid, config_dict):
    pc = PC.objects.get(uid=pc_uid)
    if not pc.is_active:
        return 0

    # We need two config dicts: one from the PC itself and one from groups
    # and global configuration
    config_lists = pc.get_list_of_configurations()

    pc_config_list = config_lists.pop()

    pc_config = {}
    for entry in pc_config_list.entries.all():
        pc_config[entry.key] = entry.value

    others_config = {}
    for conf in config_lists:
        for entry in conf.entries.all():
            others_config[entry.key] = entry.value

    for key, value in config_dict.items():
        # Special case: If the value we want is in others_config, we just have
        # to remove any pc-specific config:
        if key in others_config and others_config[key] == value:
            if key in pc_config:
                pc.configuration.remove_entry(key)
        else:
            pc.configuration.update_entry(key, value)

    return True
