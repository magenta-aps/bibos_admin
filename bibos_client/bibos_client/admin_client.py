import os
import csv
import xmlrpclib


class BibOSAdmin(object):
    """XML-RPC client class for communicating with admin system."""

    def __init__(self, url, verbose=False):
        """Set up server proxy."""
        # TODO: Modify to use SSL.
        self._url = url
        self._rpc_srv = xmlrpclib.ServerProxy(self._url, verbose=verbose,
                                              allow_none=True)

    def register_new_computer(self, name, uid, distribution, site,
                              configuration):
        return self._rpc_srv.register_new_computer(
            name, uid, distribution, site, configuration
        )

    def send_status_info(self, pc_uid, package_data, job_data):
        return self._rpc_srv.send_status_info(pc_uid, package_data, job_data)

    def get_instructions(self, pc_uid):
        return self._rpc_srv.get_instructions(pc_uid)


if __name__ == '__main__':
    """Simple test suite."""
    import netifaces
    from bibos_utils.bibos_config import BibOSConfig

    admin_url = 'http://localhost:8080/admin-xml/'
    bibos_config_file = '/etc/bibos/bibos.conf'
    bibos_config = BibOSConfig(bibos_config_file)

    admin = BibOSAdmin(admin_url)

    # Find HW address to use as UID
    try:
        addrs = netifaces.ifaddresses('eth0')
        mac = netifaces.ifaddresses('eth0')[netifaces.AF_LINK][0]['addr']
        uid = mac
    except:
        # Don't use mac address, generate random number instead
        uid = 'pop'
    print admin.register_new_computer('pip', uid, 'BIBOS', 'AAKB',
                                      bibos_config.get_data())

    # Find list of all packages for status.
    #os.system('get_package_data /tmp/packages.csv')

    with open('/tmp/packages.csv') as f:
        package_reader = csv.reader(f, delimiter=';')
        package_data = [p for p in package_reader]

    print admin.send_status_info(uid, package_data, None)

    print admin.get_instructions('pop')
