
import xmlrpclib


class BibOSAdmin(object):
    """XML-RPC client class for communicating with admin system."""

    def __init__(self, url, verbose=False):
        """Set up server proxy."""
        # TODO: Modify to use SSL.
        self._url = url
        self._rpc_srv = xmlrpclib.ServerProxy(self._url, verbose=verbose,
                                              allow_none=True)

    def register_new_computer(self, name, uid, distribution, site):
        return self._rpc_srv.register_new_computer(
            name, uid, distribution, site
        )

    def send_status_info(self, pc_uid, package_data, job_data):
        return self._rpc_srv.send_status_info(pc_uid, package_data, job_data)

    def get_instructions(self, pc_uid):
        return self._rpc_srv.get_instructions(pc_uid)

if __name__ == '__main__':
    """Simple test suite."""
    admin_url = 'http://localhost:8080/admin-xml/'

    admin = BibOSAdmin(admin_url)

    print admin.register_new_computer('pip', 'pop', 'BibOS', 'AAKB')

    print admin.send_status_info('pop', None, None)

    print admin.get_instructions('pop')
