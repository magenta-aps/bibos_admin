import os
import csv
import xmlrpclib
import urllib2


def get_default_admin(verbose=False):
    conf_data = BibOSConfig().get_data()
    admin_url = conf_data.get('admin_url', 'http://bibos.magenta-aps.dk')
    xml_rpc_url = conf_data.get('xml_rpc_url', '/admin-xml/')
    return BibOSAdmin(''.join([admin_url, xml_rpc_url]), verbose=verbose)


# Thanks to A. Ellerton for this
class ProxyTransport(xmlrpclib.Transport):
    """Provides an XMl-RPC transport routing via a http proxy.

    This is done by using urllib2, which in turn uses the environment
    varable http_proxy and whatever else it is built to use (e.g. the
    windows registry).

    NOTE: the environment variable http_proxy should be set correctly.
    See checkProxySetting() below.

    Written from scratch but inspired by xmlrpc_urllib_transport.py
    file from http://starship.python.net/crew/jjkunce/ byself,  jjk.

    A. Ellerton 2006-07-06
    """

    def __init__(self, schema='http'):
        xmlrpclib.Transport.__init__(self)
        self.schema = schema

    def request(self, host, handler, request_body, verbose):

        self.verbose = verbose
        url = self.schema + '://' + host + handler

        request = urllib2.Request(url)
        request.add_data(request_body)

        # Note: 'Host' and 'Content-Length' are added automatically
        request.add_header("User-Agent", self.user_agent)
        request.add_header("Content-Type", "text/xml")  # Important

        proxy_handler = urllib2.ProxyHandler()
        opener = urllib2.build_opener(proxy_handler)
        f = opener.open(request)
        return(self.parse_response(f))


class BibOSAdmin(object):
    """XML-RPC client class for communicating with admin system."""

    def __init__(self, url, verbose=False):
        """Set up server proxy."""
        # TODO: Modify to use SSL.
        self._url = url
        rpc_args = {'verbose': verbose, 'allow_none': True}
        # Use proxy if present
        if 'http_proxy' in os.environ:
            rpc_args['transport'] = ProxyTransport(
                schema=url[:url.index(':')]
            )

        self._rpc_srv = xmlrpclib.ServerProxy(self._url, **rpc_args)

    def register_new_computer(self, mac, name, distribution, site,
                              configuration):
        return self._rpc_srv.register_new_computer(
            mac, name, distribution, site, configuration
        )

    def upload_dist_packages(self, distribution_uid, package_data):
        return self._rpc_srv.upload_dist_packages(distribution_uid,
                                                  package_data)

    def send_status_info(self, pc_uid, package_data, job_data,
                         update_required=None):
        return self._rpc_srv.send_status_info(pc_uid, package_data, job_data,
                                              update_required)

    def get_instructions(self, pc_uid, update_data):
        return self._rpc_srv.get_instructions(pc_uid, update_data)

    def get_proxy_setup(self, pc_uid):
        return self._rpc_srv.get_proxy_setup(pc_uid)

    def push_config_keys(self, pc_uid, config_dict):
        return self._rpc_srv.push_config_keys(pc_uid, config_dict)

    def push_security_events(self, pc_uid, csv_data):
        return self._rpc_srv.push_security_events(pc_uid, csv_data)


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
    # os.system('get_package_data /tmp/packages.csv')

    with open('/tmp/packages.csv') as f:
        package_reader = csv.reader(f, delimiter=';')
        package_data = [p for p in package_reader]

    print admin.send_status_info(uid, package_data, None)

    print admin.get_instructions('pop')
