from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.models import User

from system.models import PC, Site

import datetime
import random
import string
import re
import os.path


class Script(models.Model):
    """A script to be performed on a registered client computer."""
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), max_length=4096)
    site = models.ForeignKey(Site, related_name='scripts',
                             null=True, blank=True)
    # The executable_code field should contain a single executable (e.g. a Bash
    # script OR a single extractable .zip or .tar.gz file with all necessary
    # data.
    executable_code = models.FileField(_('executable code'),
                                       upload_to='script_uploads')
    is_security_script = models.BooleanField(_('security script'),
                                             default=False, null=False)

    @property
    def is_global(self):
        return self.site is None

    def __unicode__(self):
        return self.name

    @staticmethod
    def get_system_script(name):
        try:
            script = Script.objects.get(description=name)
        except Script.DoesNotExist:
            system_site = Site.get_system_site()

            full_script_path = os.path.join(
                settings.MEDIA_ROOT,
                'system_scripts/',
                name
            )

            if(os.path.isfile(full_script_path)):
                args = []
                title = name
                title_matcher = re.compile('BIBOS_SCRIPT_TITLE:\s*([^\n]+)')
                arg_matcher = re.compile(
                    'BIBOS_SCRIPT_ARG:(' +
                    '|'.join([v for v, n in Input.VALUE_CHOICES]) +
                    ')',
                    flags=re.IGNORECASE
                )

                fh = open(full_script_path, 'r')
                for line in fh.readlines():
                    m = arg_matcher.search(line)
                    if m is not None:
                        args.append(m.group(1).upper())
                    else:
                        m = title_matcher.search(line)
                        if m is not None:
                            title = m.group(1)
                fh.close()

                script = Script.objects.create(
                    name=title,
                    description=name,
                    executable_code='system_scripts/' + name,
                    site=system_site
                )
                script.save()

                for position, vtype in enumerate(args):
                    Input.objects.create(
                        name=script.name + " arg " + str(position + 1),
                        position=position,
                        value_type=vtype,
                        mandatory=True,
                        script=script
                    )
            else:
                script = None
        return script

    def run_on(self, site, pc_list, *args):
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        batch = Batch(site=site, script=self,
                      name=' '.join([self.name, now_str]))
        batch.save()

        # Add parameters
        for i, inp in enumerate(self.inputs.all().order_by('position')):
            if i < len(args):
                value = args[i]
                if(inp.value_type == Input.FILE):
                    p = Parameter(input=inp, batch=batch, file_value=value)
                else:
                    p = Parameter(input=inp, batch=batch, string_value=value)
                p.save()

        for pc in pc_list:
            job = Job(batch=batch, pc=pc)
            job.save()

        return batch

    def run_on_pc(self, pc, *args):
        return self.run_on(pc.site, [pc], *args)

    def get_absolute_url(self, **kwargs):
        if 'site_uid' in kwargs:
            site_uid = kwargs['site_uid']
        else:
            site_uid = self.site.uid
        return reverse('script', args=(site_uid, self.pk))


class Batch(models.Model):
    """A batch of jobs to be performed on a number of computers."""

    # TODO: The name should probably be generated automatically from ID and
    # script and date, etc.
    name = models.CharField(_('name'), max_length=255)
    script = models.ForeignKey(Script)
    site = models.ForeignKey(Site, related_name='batches')

    def __unicode__(self):
        return self.name


class Job(models.Model):
    """A Job or task to be performed on a single computer."""

    # Job status choices
    NEW = 'NEW'
    SUBMITTED = 'SUBMITTED'
    RUNNING = 'RUNNING'
    DONE = 'DONE'
    FAILED = 'FAILED'
    RESOLVED = 'RESOLVED'

    STATUS_TRANSLATIONS = {
        NEW: _('jobstatus:New'),
        SUBMITTED: _('jobstatus:Submitted'),
        RUNNING: _('jobstatus:Running'),
        FAILED: _('jobstatus:Failed'),
        DONE: _('jobstatus:Done'),
        RESOLVED: _('jobstatus:Resolved')
    }

    STATUS_CHOICES = (
        (NEW, STATUS_TRANSLATIONS[NEW]),
        (SUBMITTED, STATUS_TRANSLATIONS[SUBMITTED]),
        (RUNNING, STATUS_TRANSLATIONS[RUNNING]),
        (FAILED, STATUS_TRANSLATIONS[FAILED]),
        (DONE, STATUS_TRANSLATIONS[DONE]),
        (RESOLVED, STATUS_TRANSLATIONS[RESOLVED])
    )

    STATUS_TO_LABEL = {
        NEW: '',
        SUBMITTED: 'label-info',
        RUNNING: 'label-warning',
        DONE: 'label-success',
        FAILED: 'label-important',
        RESOLVED: 'label-success'
    }

    # Fields
    # Use built-in ID field for ID.
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              default=NEW)
    log_output = models.CharField(_('log output'),
                                  max_length=128000,
                                  blank=True)
    started = models.DateTimeField(_('started'), null=True)
    finished = models.DateTimeField(_('finished'), null=True)
    batch = models.ForeignKey(Batch, related_name='jobs')
    pc = models.ForeignKey(PC, related_name='jobs')

    def __unicode__(self):
        return '_'.join(map(unicode, [self.batch, self.id]))

    @property
    def has_info(self):
        return self.status == Job.FAILED or len(self.log_output) > 1

    @property
    def status_label(self):
        if self.status is None:
            return ''
        else:
            return Job.STATUS_TO_LABEL[self.status]

    @property
    def status_translated(self):
        if self.status is None:
            return ''
        else:
            return Job.STATUS_TRANSLATIONS[self.status]

    @property
    def failed(self):
        return self.status == Job.FAILED

    @property
    def as_instruction(self):
        parameters = []

        for param in self.batch.parameters.order_by("input__position"):
            parameters.append({
                'type': param.input.value_type,
                'value': param.transfer_value
            })

        return {
            'id': self.pk,
            'status': self.status,
            'parameters': parameters,
            'executable_code': self.batch.script.executable_code.read()
        }

    def resolve(self):
        if self.failed:
            self.status = Job.RESOLVED
            self.save()
        else:
            raise Exception(_('Cannot change status from {0} to {1}').format(
                self.status,
                Job.RESOLVED
            ))

    def restart(self):
        if not self.failed:
            raise Exception(_('Can only restart jobs with status %s') % (
                Job.FAILED
            ))
        # Create a new batch
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        script = self.batch.script
        new_batch = Batch(site=self.batch.site, script=script,
                          name=' '.join([script.name, now_str]))
        new_batch.save()
        for p in self.batch.parameters.all():
            new_p = Parameter(
                input=p.input,
                batch=new_batch,
                file_value=p.file_value,
                string_value=p.string_value
            )
            new_p.save()
        new_job = Job(batch=new_batch, pc=self.pc)
        new_job.save()
        self.resolve()

        return new_job


class Input(models.Model):
    """Input for a script"""

    # Value types
    STRING = 'STRING'
    INT = 'INT'
    DATE = 'DATE'
    FILE = 'FILE'

    VALUE_CHOICES = (
        (STRING, _('String')),
        (INT, _('Integer')),
        (DATE, _('Date')),
        (FILE, _('File'))
    )

    name = models.CharField(_('name'), max_length=255)
    value_type = models.CharField(_('value type'), choices=VALUE_CHOICES,
                                  max_length=10)
    position = models.IntegerField(_('position'))
    mandatory = models.BooleanField(_('mandatory'), default=True)
    script = models.ForeignKey(Script, related_name='inputs')

    def __unicode__(self):
        return self.name


def upload_file_name(instance, filename):
    size = 32
    random_dirname = ''.join(
        random.choice(
            string.ascii_lowercase + string.digits
        ) for x in range(size)
    )
    return '/'.join(['parameter_uploads', random_dirname, filename])


class Parameter(models.Model):
    """An input parameter for a job, a script, etc."""

    string_value = models.CharField(max_length=4096, null=True, blank=True)
    file_value = models.FileField(upload_to=upload_file_name,
                                  null=True,
                                  blank=True)
    # which input does this belong to?
    input = models.ForeignKey(Input)
    # and which batch are we running?
    batch = models.ForeignKey(Batch, related_name='parameters')

    @property
    def transfer_value(self):
        input_type = self.input.value_type
        if input_type == Input.FILE:
            return self.file_value.url
        else:
            return self.string_value


class SecurityProblem(models.Model):
    """A security problem and the method (script) to handle it."""

    # Problem levels.

    NORMAL = 'Normal'
    HIGH = 'High'
    CRITICAL = 'Critical'

    LEVEL_TRANSLATIONS = {
        NORMAL: _('securitylevel:Normal'),
        HIGH: _('securitylevel:High'),
        CRITICAL: _('securitylevel:Critical'),
    }

    LEVEL_CHOICES = (
        (NORMAL, LEVEL_TRANSLATIONS[NORMAL]),
        (HIGH, LEVEL_TRANSLATIONS[HIGH]),
        (CRITICAL, LEVEL_TRANSLATIONS[CRITICAL]),
    )

    LEVEL_TO_LABEL = {
        NORMAL: 'label-success',
        HIGH: 'label-warning',
        CRITICAL: 'label-important',
    }

    name = models.CharField(_('name'), max_length=255)
    uid = models.CharField(_('uid'), max_length=255)
    description = models.CharField(_('description'), max_length=1024,
                                   blank=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES,
                             default=HIGH)
    site = models.ForeignKey(Site, related_name='security_problems')
    script = models.ForeignKey(Script, related_name='security_problems')


class SecurityEvent(models.Model):
    """A security event is an instance of a security problem."""

    # Event status choices
    NEW = 'NEW'
    ASSIGNED = 'ASSIGNED'
    RESOLVED = 'RESOLVED'

    STATUS_TRANSLATIONS = {
        NEW: _('eventstatus:New'),
        ASSIGNED: _('eventstatus:Assigned'),
        RESOLVED: _('eventstatus:Resolved')
    }

    STATUS_CHOICES = (
        (NEW, STATUS_TRANSLATIONS[NEW]),
        (ASSIGNED, STATUS_TRANSLATIONS[ASSIGNED]),
        (RESOLVED, STATUS_TRANSLATIONS[RESOLVED])
    )

    STATUS_TO_LABEL = {
        NEW: 'label-important',
        ASSIGNED: 'label-warning',
        RESOLVED: 'label-success'
    }
    problem = models.ForeignKey(SecurityProblem, null=False)
    # The time the problem was reported in the log file
    ocurred_time = models.DateTimeField(_('occurred'))
    # The time the problem was submitted to the system
    reported_time = models.DateTimeField(_('reported'))
    pc = models.ForeignKey(PC)
    summary = models.CharField(max_length=4096, null=False, blank=False)
    complete_log = models.TextField(null=True, Blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              default=NEW)
    assigned_user = models.ForeignKey(User, null=True, Blank=True)
