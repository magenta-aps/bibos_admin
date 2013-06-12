# This module contains the implementation of the XML-RPC API used by the
# client.

import datetime

from models import PC, Site, Distribution, Configuration, ConfigurationEntry
from models import PackageList, Package
from job.models import Job
from django.db.models import Q


def register_new_computer(name, uid, distribution, site, configuration):
    """Register a new computer with the admin system - after registration, the
    computer will be submitted for approval."""

    try:
        new_pc = PC.objects.get(uid=uid)
        package_list = new_pc.package_list
    except PC.DoesNotExist:
        new_pc = PC(name=name, uid=uid)
        new_pc.site = Site.objects.get(uid=site)
        # TODO: Better to enforce existence of package list in constructor.
        package_list = PackageList(name=name, uid=uid)

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
    # Set and save PmC.
    new_pc.configuration = my_config
    package_list.save()
    new_pc.package_list = package_list
    new_pc.save()
    return 0


def send_status_info(pc_uid, package_data, job_data):
    """Update package lists as well as the status of outstanding jobs.
    If no updates of package or job data, these will be None. In that
    case, this function really works as an "I'm alive" signal."""

    # TODO: Code this

    # 1. Lookup PC, update "last_seen" field
    pc = PC.objects.get(uid=pc_uid)
    pc.last_seen = datetime.datetime.now()
    pc.save()

    if package_data is not None:
        # 2. Update package lists with package data
        # Clear existing packages
        pc.package_list.packages.clear()

        # Insert new ones
        # package_data is a list of dicts with the correct field names.
        for pd in package_data:
            # First, assume package & version already exists.
            try:
                p = Package.objects.get(name=pd['name'], version=pd['version'])
                pc.package_list.packages.add(p)
            except Package.DoesNotExist:
                p = pc.package_list.packages.create(
                    name=pd['name'],
                    version=pd['version'],
                    status=pd['status'],
                    description=pd['description']
                )

    # 3. Update jobs with job data
    if job_data is not None:
        for jd in job_data:
            job = Job.objects.get(pk=jd['id'])
            job.status = jd['status']
            job.started = jd['started']
            job.finished = jd['finished']
            job.log_output = jd['log_output']
            job.save()

    return 0


import os


def get_instructions(pc_uid):
    """This function will ask for new instructions in the form of a list of
    jobs, which will be scheduled for execution and executed upon receipt.
    These jobs will generally take the form of bash scripts."""

    pc = PC.objects.get(uid=pc_uid)
    pc.last_seen = datetime.datetime.now()
    pc.save()

    jobs = []

    # TODO: Retrieve non-submitted jobs, mark them as subitted and send to the
    # client denoted by UID.

    for job in pc.jobs.filter(status=Job.NEW):
        parameters = []

        for param in job.batch.parameters.order_by("input__position"):
            parameters.append({
                'type': param.input.value_type,
                'value': param.transfer_value
            })

        job.status = Job.SUBMITTED
        job.save()

        jobs.append({
            'id': job.pk,
            'status': job.status,
            'parameters': parameters,
            'executable_code': job.batch.script.executable_code.read()
        })

    return jobs
