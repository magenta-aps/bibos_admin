# This module contains the implementation of the XML-RPC API used by the
# client.

from models import PC, Site


def register_new_computer(name, uid, distribution, site):
    """Register a new computer with the admin system - after registration, the
    computer will be submitted for approval."""
    new_pc = PC()
    new_pc.name = name
    new_pc.uid = uid
    # Set to correct site etc. as well
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
