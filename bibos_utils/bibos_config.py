import yaml
import sys

DEFAULT_CONFIG_FILE = "/etc/bibos/bibos.conf"


def get_config(key, filename=DEFAULT_CONFIG_FILE):
    """Get value of a known config key."""
    conf = BibOSConfig(filename)
    try:
        return conf.get_value(key)
    except:
        return None


def set_config(key, value, filename=DEFAULT_CONFIG_FILE):
    """Set value of a config key."""
    conf = BibOSConfig(filename)
    try:
        val = conf.set_value(key, value)
        conf.save()
        return val
    except Exception as inst:
        print >> sys.stderr, "Error: ", str(inst)
        return None


class BibOSConfig():
    def __init__(self, filename=DEFAULT_CONFIG_FILE):
        """Create new configuration object. Each configuration object is
        defined by its ownership of exactly one configuration file."""
        self.filename = filename
        self.yamldata = {}
        # Do not catch exceptions here, let them pass from load function
        self.load()

    def load(self):
        """Load a configuration - initialize to empty configuration if file
        does not exist."""
        try:
            stream = open(self.filename, "r")
            self.yamldata = yaml.load(stream)
        except IOError as e:
            if e.errno == 2:
                # File does not exist -> empty YAML dictionary.
                self.yamldata = {}
            else:
                # Something else is wrong, e.g. errno 13 = permission denied.
                # Pass the buck.
                raise
        return self


    def save(self):
        try:
            stream = open(self.filename, "w")
        except IOError as e: 
            print "Error opening BibOSConfig file for writing: ", str(e)

        yaml.dump(self.yamldata, stream, default_flow_style=False)

        return self

    def set_value(self, key, value):
        current = self.yamldata

        i = key.find(".")
        while (i != -1):
            subkey = key[:i]
            try:
                current = current[subkey]
            except KeyError:
                current[subkey] = {}
                current = current[subkey]
            key = key[i + 1:]
            i = key.find(".")

        current[key] = value

        return self

    def get_value(self, key):
        current = self.yamldata

        i = key.find(".")
        while (i != -1):
            subkey = key[:i]
            current = current[subkey]
            key = key[i + 1:]
            i = key.find(".")

        return current[key]

    def get_data(self):
        return self.yamldata
