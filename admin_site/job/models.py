from django.db import models
from django.utils.translation import ugettext_lazy as _

from system.models import PC, Site


class Script(models.Model):
    """A script to be performed on a registered client computer."""
    name = models.CharField(_('name'), max_length=255)
    description = models.CharField(_('description'), max_length=1024)
    site = models.ForeignKey(Site, related_name='scripts',
                             null=True, blank=True)
    # The executable_code field should contain a single executable (e.g. a Bash
    # script OR a single extractable .zip or .tar.gz file with all necessary
    # data.
    executable_code = models.FileField(_('executable code'),
                                       upload_to='site_media/script_uploads')

    def __unicode__(self):
        return self.name


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
    STATUS_CHOICES = (
        (NEW, _('New')),
        (SUBMITTED, _('Submitted')),
        (RUNNING, _('Running')),
        (DONE, _('Done')),
        (FAILED, _('Failed'))
    )

    STATUS_TO_LABEL = {
        NEW: '',
        SUBMITTED: 'label-info',
        RUNNING: 'label-warning',
        DONE: 'label-success',
        FAILED: 'label-important'
    }

    # Fields
    # Use built-in ID field for ID.
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              default=NEW)
    log_output = models.CharField(_('log output'), max_length=4096, blank=True)
    started = models.DateTimeField(_('started'), null=True)
    finished = models.DateTimeField(_('finished'), null=True)
    batch = models.ForeignKey(Batch, related_name='jobs')
    pc = models.ForeignKey(PC, related_name='jobs')

    def __unicode__(self):
        return '_'.join(map(unicode, [self.batch, self.id]))


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

    name = models.CharField(_('name'), max_length=255, unique=True)
    value_type = models.CharField(_('value type'), choices=VALUE_CHOICES,
                                  max_length=10)
    position = models.IntegerField(_('position'))
    mandatory = models.BooleanField(_('mandatory'), default=True)
    script = models.ForeignKey(Script)

    def __unicode__(self):
        return self.name


class Parameter(models.Model):
    """An input parameter for a job, a script, etc."""

    string_value = models.CharField(max_length=4096, null=True, blank=True)
    file_value = models.FileField(upload_to='site_media/parameter_uploads',
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
