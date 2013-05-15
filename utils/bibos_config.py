import yaml

DEFAULT_CONFIG_FILE = "/etc/bibos/bibos.conf"


def get_config(key, filename=DEFAULT_CONFIG_FILE):
    conf = BibOSConfig(filename)
    try:
        return conf.get_value(key)
    except:
        return None


def set_config(key, value, filename=DEFAULT_CONFIG_FILE):
    conf = BibOSConfig(filename)
    try:
        val = conf.set_value(key, value)
        conf.save()
        return val
    except:
        return None


class BibOSConfig():
    def __init__(self, filename=DEFAULT_CONFIG_FILE):
        self.filename = filename
        self.load()

    def load(self, filename=None):
        if filename is None:
            filename = self.filename

        if filename is None:
            self.yamldata = {}
        else:
            stream = file(filename, "r")
            self.yamldata = yaml.load(stream)

        return self

    def save(self, filename=None):
        if filename is None:
            filename = self.filename

        stream = file(filename, "w")
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
