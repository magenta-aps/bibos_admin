
import os
import os.path
import stat
import urllib2
import json
import datetime
import urlparse
import glob
import re
import subprocess
from lockfile import FileLock, AlreadyLocked

from bibos_utils.bibos_config import BibOSConfig

from admin_client import BibOSAdmin
from utils import upload_packages

"""
Directory structure for storing BibOS jobs:
/var/lib/bibos/jobs/<id> - Files related to job with id <id>
/var/lib/bibos/jobs/<id>/attachments - files needed to execute the job
/var/lib/bibos/jobs/<id>/executable - the program that executes the job
/var/lib/bibos/jobs/<id>/parameters.json - json file containing parameters
/var/lib/bibos/jobs/<id>/status - status file, created by the runtime system
/var/lib/bibos/jobs/<id>/started - created when job is stated
/var/lib/bibos/jobs/<id>/finished - created when job is finished/failed
/var/lib/bibos/jobs/<id>/output.log - Logfile with output from the job
"""

JOBS_DIR = '/var/lib/bibos/jobs'
LOCK = FileLock(JOBS_DIR + '/running')


class LocalJob(dict):
    def __init__(self, id=None, path=None, data=None):
        if id is None and data is not None and 'id' in data:
            id = data['id']
            del data['id']

        if id is None and path is None:
            raise ValueError("You must specify either an id or a path")

        if id is not None:
            self.id = id
        else:
            # Remove trailing slash
            if path[-1] == '/':
                path = path[:-1]

            print path
            # Find id from last part of path
            m = re.match(".*/(\d+)$", path)
            if m is None:
                raise ValueError("%s is not a valid path" % path)
            else:
                self.id = m.group(1)

        if not os.path.isdir(self.path):
            os.mkdir(self.path)

        # Initialize with given data
        if data is not None:
            self.populate(data)

    @property
    def path(self):
        return JOBS_DIR + '/' + str(self.id)

    @property
    def attachments_path(self):
        return self.path + '/attachments'

    @property
    def executable_path(self):
        return self.path + '/executable'

    @property
    def parameters_path(self):
        return self.path + '/parameters.json'

    @property
    def status_path(self):
        return self.path + '/status'

    @property
    def started_path(self):
        return self.path + '/started'

    @property
    def finished_path(self):
        return self.path + '/finished'

    @property
    def log_path(self):
        return self.path + '/output.log'

    @property
    def report_data(self):
        self.load_from_path()
        result = {'id': self.id}
        for k in ['status', 'started', 'finished', 'log_output']:
            result[k] = self[k]
        return result

    def set_status(self, value):
        self['status'] = value
        self.save_property_to_file('status', self.status_path)

    def mark_started(self):
        self['started'] = str(datetime.datetime.now())
        self.save_property_to_file('started', self.started_path)

    def mark_finished(self):
        self['finished'] = str(datetime.datetime.now())
        self.save_property_to_file('finished', self.finished_path)

    def load_local_parameters(self):
        self.read_property_from_file('json_params',
                                     self.parameters_path)
        if 'json_params' in self:
            self['local_parameters'] = json.loads(self['json_params'])
            del self['json_params']
        else:
            self['local_parameters'] = []

    def load_from_path(self, full_info=False):
        if not os.path.isdir(self.path):
            raise ValueError("%s is not a directory" % self.path)

        self.read_property_from_file('status', self.status_path)
        self.read_property_from_file('started', self.started_path)
        self.read_property_from_file('finished', self.finished_path)
        self.read_property_from_file('log_output', self.log_path)

        if full_info is not False:
            self.read_property_from_file('executable_code',
                                         self.executable_path)
            self.load_local_parameters()

    def read_property_from_file(self, prop, file_path):
        try:
            fh = open(file_path, 'r')
            self[prop] = fh.read()
            fh.close()
        except IOError:
            pass

    def save_property_to_file(self, prop, file_path):
        if(prop in self):
            fh = open(file_path, 'w')
            fh.write(self[prop])
            fh.close()

    def populate(self, data):
        for k in data.keys():
            self[k] = data[k]

    def save(self):
        self.save_property_to_file('executable_code', self.executable_path)
        self.save_property_to_file('status', self.status_path)
        self.save_property_to_file('started', self.started_path)
        self.save_property_to_file('finished', self.finished_path)

        # Make sure executable is executable
        if os.path.exists(self.executable_path):
            os.chmod(self.executable_path, stat.S_IRWXU)

        self.translate_parameters()
        if 'local_parameters' in self:
            param_fh = open(self.parameters_path, 'w')
            param_fh.write(json.dumps(self['local_parameters']))
            param_fh.close()

    def translate_parameters(self):
        if not 'parameters' in self:
            return

        config = BibOSConfig()
        admin_url = config.get_value('admin_url')

        local_params = []
        self['local_parameters'] = local_params
        params = self['parameters']
        del self['parameters']
        for param in params:
            if param['type'] == 'FILE':
                # Make sure we have the directory
                if not os.path.isdir(self.attachments_path):
                    os.mkdir(self.attachments_path)

                value = param['value']
                basename = value[value.rindex('/') + 1:]
                filename = self.attachments_path + '/' + basename
                # TODO this is probably not the right URL
                full_url = urlparse.urljoin(admin_url, value)
                remote_file = urllib2.urlopen(full_url)
                attachment_fh = open(filename, 'w')
                attachment_fh.write(remote_file.read())
                attachment_fh.close()
                local_params.append(filename)
            else:
                local_params.append(param['value'])

    def log(self, message):
        fh = open(self.log_path, 'a')
        fh.write(message)
        fh.close()

    def logline(self, message):
        self.log(message + "\n")

    def run(self):
        if LOCK.i_am_locking():
            self.read_property_from_file('status', self.status_path)
            if self['status'] != 'SUBMITTED':
                os.sys.stderr.write(
                    "Job %s: Will only run jobs with status %s\n" % (
                        self.id,
                        self['status']
                    )
                )
                return
            log = open(self.log_path, 'a')
            self.load_local_parameters()
            self.set_status('RUNNING')
            cmd = [self.executable_path]
            cmd.extend(self['local_parameters'])
            self.mark_started()
            log.write(
                ">>> Starting process '%s' with arguments [%s] at %s\n" % (
                    self.executable_path,
                    ', '.join(self['local_parameters']),
                    self['started']
                )
            )
            log.flush()
            ret_val = subprocess.call(cmd, stdout=log, stderr=log)
            self.mark_finished()
            log.flush()
            if ret_val == 0:
                self.set_status('DONE')
                log.write(">>> Succeeded at %s\n" % self['finished'])
            else:
                self.set_status('FAILED')
                log.write(">>> Failed with exit status %s at %s\n" % (
                    ret_val,
                    self['finished'])
                )
            log.close()
        else:
            print >>os.sys.stderr, "Will not run job without aquired lock"


def get_url_and_uid():
    config = BibOSConfig()
    uid = config.get_value('uid')
    config_data = config.get_data()
    admin_url = config_data.get('admin_url', 'http://bibos.magenta-aps.dk/')
    xml_rpc_url = config_data.get('xml_rpc_url', '/admin-xml/')
    rpc_url = urlparse.urljoin(admin_url, xml_rpc_url)
    return(rpc_url, uid)


def import_new_jobs():
    (remote_url, uid) = get_url_and_uid()
    remote = BibOSAdmin(remote_url)
    jobs, do_send_package_info = remote.get_instructions(uid)

    for j in jobs:
        local_job = LocalJob(data=j)
        local_job.save()
        local_job.logline("Job imported at %s" % datetime.datetime.now())

    if do_send_package_info:
        try:
            # Send full package info to server.
            upload_packages()
        except Exception as e:
            print >>os.sys.stderr, "Package upload failed" + str(e)


def check_outstanding_packages():
    # Get number of packages with updates and number of security updates.
    # This is really a wrapper for apt-check.
    try:
        proc = subprocess.Popen(["/usr/lib/update-notifier/apt-check"],
                                stderr=subprocess.PIPE, shell=True)
        _, err = proc.communicate()
        package_updates, security_updates = map(int, err.split(';'))
        return (package_updates, security_updates)
    except Exception as e:
        print >>os.sys.stderr, "apt-check failed" + str(e)
        return None


def report_job_results(joblist):
    if len(joblist) < 1:
        return
    (remote_url, uid) = get_url_and_uid()
    remote = BibOSAdmin(remote_url)
    remote.send_status_info(uid, None, joblist,
                            update_required=check_outstanding_packages())


def get_pending_job_dirs():
    result = []
    for filename in glob.glob(JOBS_DIR + '/*/status'):
        fh = open(filename, 'r')
        if fh.read() == 'SUBMITTED':
            result.append(filename[:filename.rindex('/')])
    return result


def run_pending_jobs():
    dirs = get_pending_job_dirs()
    if len(dirs) < 1:
        return
    if LOCK.i_am_locking():
        results = []

        for d in dirs:
            job = LocalJob(path=d)
            job.run()
            results.append(job.report_data)

        report_job_results(results)

    else:
        print >>os.sys.stderr, "Aquire the lock before running jobs"


def update_and_run():
    try:
        LOCK.acquire(0)
        try:
            import_new_jobs()
            run_pending_jobs()
        finally:
            LOCK.release()
    except AlreadyLocked:
        print "Couldn't get lock"


if __name__ == '__main__':
    update_and_run()
