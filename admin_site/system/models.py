from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User


class Configuration(models.Model):
    """This class contains/represents the configuration of a Site, a
    Distribution, a PC Group or a PC."""
    # Doesn't need any actual fields, it seems. Should not exist independently
    # of the classes to which it may be aggregated.
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name


class ConfigurationEntry(models.Model):
    """A single configuration entry - always part of an entire
    configuration."""
    key = models.CharField(max_length=15)
    value = models.CharField(max_length=255)
    owner_configuration = models.ForeignKey(
        Configuration,
        related_name='owner',
        verbose_name=_('owner configuration')
    )


class PackageList(models.Model):
    """A list of packages to be installed on a PC or to be included in a
    distribution."""
    name = models.CharField(_('name'), max_length=255)
    uid = models.CharField(_('id'), max_length=255)

    def __unicode__(self):
        return self.name


class Site(models.Model):
    """A site which we wish to admin"""
    name = models.CharField(_('name'), max_length=255)
    uid = models.CharField(_('uid'), max_length=255, unique=True)
    users = models.ManyToManyField(User,
                                   related_name='site_users',
                                   verbose_name=_('Site Users'),
                                   blank=True)
    configuration = models.ForeignKey(Configuration)

    def __unicode__(self):
        return self.name


class Distribution(models.Model):
    """This represents a GNU/Linux distribution managed by us."""
    name = models.CharField(_('name'), max_length=255)
    uid = models.CharField(_('uid'), max_length=255)
    configuration = models.ForeignKey(Configuration)
    package_list = models.ForeignKey(PackageList)

    def __unicode__(self):
        return self.name


class Package(models.Model):
    """This class represents a single Debian package to be installed."""
    name = models.CharField(_('name'), max_length=255)
    uid = models.CharField(_('uid'), max_length=255)
    version = models.CharField(_('version'), max_length=255)
    package_list = models.ForeignKey(PackageList,
                                     related_name='package_list',
                                     verbose_name=_('package list'))


class PCGroup(models.Model):
    """Groups of PCs. Each PC may be in zero or many groups."""
    name = models.CharField(_('name'), max_length=255)
    uid = models.CharField(_('id'), max_length=255)

    def __unicode__(self):
        return self.name


class PC(models.Model):
    """This class represents one PC, i.e. one client of the admin system."""
    name = models.CharField(_('name'), max_length=255)
    uid = models.CharField(_('uid'), max_length=255)
    description = models.CharField(_('description'), max_length=1024,
                                   blank=True)
    distribution = models.ForeignKey(Distribution)
    configuration = models.ForeignKey(Configuration)
    pc_groups = models.ManyToManyField(PCGroup, related_name='pcs', blank=True)
    package_list = models.ForeignKey(PackageList)
    site = models.ForeignKey(Site)
    is_active = models.BooleanField(_('active'), default=False)
    creation_time = models.DateTimeField(_('creation time'),
        auto_now_add=True)
    last_seen = models.DateTimeField(_('last seen'), null=True, blank=True)

    def __unicode__(self):
        return self.name
