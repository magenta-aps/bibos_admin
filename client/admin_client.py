
import xmlrpclib


class BibOSAdmin(object):
    """XML-RPC client class for communicating with admin system."""
    
    def __init__(self, url, verbose=False):
        """Set up server proxy."""
        # TODO: Modify to use SSL.
        self._url = url
        self._rpc_srv = xmlrpclib.ServerProxy(self._url, verbose=verbose)

    def register_new_computer(self, name, uid, distribution, site):
        return self._rpc_srv.register_new_computer(name, uid, distribution, site)

    def send_status_info(self, pc_uid, package_data, job_data):
        return self._rpc_srv.send_status_info(pc_uid, package_data, job_data)
