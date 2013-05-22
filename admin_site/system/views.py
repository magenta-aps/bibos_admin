# Create your views here.

from models import PC, Site


# XML-RPC view - not available in GUI.
def register_new_computer(name, uid, distribution, site):
    """Register a new computer with the admin system - after registration, the
    computer will be submitted for approval."""
    new_pc = PC()
    new_pc.name = name
    new_pc.uid = uid


# XML-RPC view - not available in GUI.
def send_status_info(pc_uid, package_data, job_data):
    """Update package lists as well as the status of outstanding jobs.
    If no updates of package or job data, these will be None. In that
    case, this function really works as an "I'm alive" signal."""
    pass
