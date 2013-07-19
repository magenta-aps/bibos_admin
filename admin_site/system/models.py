from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


"""The following variables define states of objects like jobs or PCs. It is
used for labeling in the GUI."""

# States
NEW = _("New")
FAIL = _("Fail")
UPDATE = _("Update")
OK = ''

# Priorities
INFO = 'info'
WARNING = 'warning'
IMPORTANT = 'important'
NONE = ''


class Configuration(models.Model):
    """This class contains/represents the configuration of a Site, a
    Distribution, a PC Group or a PC."""
    # Doesn't need any actual fields, it seems. Should not exist independently
    # of the classes to which it may be aggregated.
    name = models.CharField(max_length=255, unique=True)

    def update_from_request(self, req_params, submit_name):
        seen_set = set()
        new_ids = []

        existing_set = set(cnf.pk for cnf in self.entries.all())

        for pk in req_params.getlist(submit_name, []):
            key_param = "%s_%s_key" % (submit_name, pk)
            value_param = "%s_%s_value" % (submit_name, pk)

            key = req_params.get(key_param, '')
            value = req_params.get(value_param, '')

            if pk.startswith("new_"):
                # Create new entry
                cnf = ConfigurationEntry(
                    key=key,
                    value=value,
                    owner_configuration=self
                )
            else:
                # Update submitted entry
                cnf = ConfigurationEntry.objects.get(pk=pk)
                cnf.key = key
                cnf.value = value
                seen_set.add(cnf.pk)

            cnf.save()

        # Delete entries that were not in the submitted data
        for pk in existing_set - seen_set:
            cnf = ConfigurationEntry.objects.get(pk=pk)
            cnf.delete()

    def remove_entry(self, key):
        return self.entries.filter(key=key).delete()

    def update_entry(self, key, value):
        try:
            e = self.entries.get(key=key)
            e.value = value
        except ConfigurationEntry.DoesNotExist:
            e = ConfigurationEntry(
                owner_configuration=self,
                key=key,
                value=value
            )
        finally:
            e.save()

    def __unicode__(self):
        return self.name


class ConfigurationEntry(models.Model):
    """A single configuration entry - always part of an entire
    configuration."""
    key = models.CharField(max_length=32)
    value = models.CharField(max_length=255)
    owner_configuration = models.ForeignKey(
        Configuration,
        related_name='entries',
        verbose_name=_('owner configuration')
    )


class Package(models.Model):
    """This class represents a single Debian package to be installed."""
    name = models.CharField(_('name'), max_length=255)
    version = models.CharField(_('version'), max_length=255)
    description = models.CharField(_('description'), max_length=255)

    def __unicode__(self):
        return ' '.join([self.name, self.version])

    class Meta:
        unique_together = ('name', 'version')


class CustomPackages(models.Model):
    """A list of packages to be installed on a PC or to be included in a
    distribution."""
    name = models.CharField(_('name'), max_length=255)
    packages = models.ManyToManyField(Package,
                                      through='PackageInstallInfo',
                                      blank=True)

    def update_by_package_names(self, addlist, removelist):
        add_packages_old = set()
        remove_packages_old = set()

        for ii in self.install_infos.all():
            if ii.do_add:
                add_packages_old.add(ii.package.name)
            else:
                remove_packages_old.add(ii.package.name)

        for oldlist, newlist, addflag in [
            (add_packages_old, set(addlist), True),
            (remove_packages_old, set(removelist), False),
        ]:
            # Add new add-packages
            for name in newlist - oldlist:
                try:
                    package = Package.objects.filter(name=name)[0]
                except IndexError:
                    package = Package.objects.create(name=name)

                ii = PackageInstallInfo(
                    custom_packages=self,
                    package=package,
                    do_add=addflag
                )
                ii.save()
            # Remove unwanted add-packages
            qs = PackageInstallInfo.objects.filter(
                do_add=addflag,
                custom_packages=self,
                package__name__in=list(oldlist - newlist)
            )
            qs.delete()

    def update_package_status(self, name, do_add):
        # Delete any old reference
        self.install_infos.filter(
            package__name=name
        ).delete()

        # And create a new
        try:
            package = Package.objects.filter(name=name)[0]
        except IndexError:
            package = Package.objects.create(name=name)

        ii = PackageInstallInfo(
            custom_packages=self,
            package=package,
            do_add=do_add
        )

        ii.save()

    def __unicode__(self):
        return self.name


class PackageInstallInfo(models.Model):
    do_add = models.BooleanField(default=True)
    package = models.ForeignKey(Package)
    custom_packages = models.ForeignKey(CustomPackages,
                                     related_name='install_infos')

    def __unicode__(self):
        return self.package.name


class PackageList(models.Model):
    """A list of packages to be installed on a PC or to be included in a
    distribution."""
    name = models.CharField(_('name'), max_length=255)
    packages = models.ManyToManyField(Package,
                                      through='PackageStatus',
                                      blank=True)

    @property
    def names_of_installed_package(self):
        return self.statuses.filter(
            Q(status__startswith='install') |
            Q(status=PackageStatus.NEEDS_UPGRADE) |
            Q(status=PackageStatus.UPGRADE_PENDING)
        ).values_list('package__name', flat=True)

    @property
    def needs_upgrade_packages(self):
        return [s.package for s in self.statuses.filter(
            status=PackageStatus.NEEDS_UPGRADE
        )]

    @property
    def pending_upgrade_packages(self):
        return [s.package for s in self.statuses.filter(
            status=PackageStatus.UPGRADE_PENDING
        )]

    def flag_for_upgrade(self, package_names):
        if len(package_names):
            qs = self.statuses.filter(
                package__name__in=package_names,
                status=PackageStatus.NEEDS_UPGRADE
            )
            num = len(qs)
            qs.update(
                status=PackageStatus.UPGRADE_PENDING
            )
            return num
        else:
            return 0

    def __unicode__(self):
        return self.name


class PackageStatus(models.Model):
    NEEDS_UPGRADE = 'needs upgrade'
    UPGRADE_PENDING = 'upgrade pending'

    # Note that dpkg can output just about anything for the status-field,
    # but installed packages will all have a status that starts with
    # 'install'

    status = models.CharField(max_length=255)
    package = models.ForeignKey(Package)
    package_list = models.ForeignKey(PackageList,
                                    related_name='statuses')

    def __unicode__(self):
        return self.package.name + u': ' + self.status


class Site(models.Model):
    """A site which we wish to admin"""
    name = models.CharField(_('name'), max_length=255)
    uid = models.CharField(_('uid'), max_length=255, unique=True)
    configuration = models.ForeignKey(Configuration)

    @staticmethod
    def get_system_site():
        try:
            site = Site.objects.get(uid='system')
        except Site.DoesNotExist:
            site = Site.objects.create(
                name='system',
                uid='system',
                configuration=Configuration.objects.create(
                    name='system_site_configuration'
                )
            )
        return site

    @property
    def users(self):
        profiles = [
            u.get_profile() for u in User.objects.all().extra(
            select={'lower_name': 'lower(username)'}
        ).order_by('lower_name')
                if u.get_profile().site == self
                and u.get_profile().type != 0
        ]
        return [p.user for p in profiles]

    @property
    def url(self):
        return self.uid

    @property
    def is_delete_allowed(self):
        """This should always be checked by the user interface to avoid
        validation errors from the pre_delete signal."""
        return self.pcs.count() == 0

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Customize behaviour when saving a site object."""
        # Before actual save
        # 1. uid should consist of lowercase letters.
        self.uid = self.uid.lower()
        # 2. Create related configuration object if necessary.
        is_new = self.id is None
        if is_new and self.configuration is None:
            try:
                self.configuration = Configuration.objects.get(
                    name=self.uid
                )
            except Configuration.DoesNotExist:
                self.configuration = Configuration.objects.create(
                    name=self.uid
                )

        # Perform save
        super(Site, self).save(*args, **kwargs)

        # After save
        pass

    def get_absolute_url(self):
        return '/site/{0}'.format(self.url)


class Distribution(models.Model):
    """This represents a GNU/Linux distribution managed by us."""
    name = models.CharField(_('name'), max_length=255)
    uid = models.CharField(_('uid'), max_length=255)
    configuration = models.ForeignKey(Configuration)
    # CustomPackages is preferrable here.
    # Maybe we'd like one distribution to inherit from another.
    package_list = models.ForeignKey(PackageList)

    def __unicode__(self):
        return self.name


class PCGroup(models.Model):
    """Groups of PCs. Each PC may be in zero or many groups."""
    name = models.CharField(_('name'), max_length=255)
    uid = models.CharField(_('id'), max_length=255, unique=True)
    description = models.TextField(_('description'), max_length=1024,
                                   null=True, blank=True)
    site = models.ForeignKey(Site, related_name='groups')
    configuration = models.ForeignKey(Configuration)
    custom_packages = models.ForeignKey(CustomPackages)

    @property
    def url(self):
        return self.uid

    @property
    def is_delete_allowed(self):
        """This should always be checked by the user interface to avoid
        validation errors from the pre_delete signal."""
        return self.pcs.count() == 0

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Customize behaviour when saving a group object."""
        # Before actual save
        is_new = self.id is None
        if is_new and self.name:
            self.uid = self.uid.lower()
            related_name = 'Group: ' + self.name
            self.configuration, new = Configuration.objects.get_or_create(
                name=related_name
            )
            self.custom_packages, new = CustomPackages.objects.get_or_create(
                name=related_name
            )
        # Perform save
        super(PCGroup, self).save(*args, **kwargs)

        # After save
        pass

    def get_absolute_url(self):
        site_url = self.site.get_absolute_url()
        return u'{0}/groups/{1}'.format(site_url, self.url)

    class Meta:
        unique_together = ('uid', 'site')
        ordering = ['name']


class PC(models.Model):
    """This class represents one PC, i.e. one client of the admin system."""
    name = models.CharField(_('name'), max_length=255)
    uid = models.CharField(_('uid'), max_length=255)
    description = models.CharField(_('description'), max_length=1024,
                                   blank=True)
    distribution = models.ForeignKey(Distribution)
    configuration = models.ForeignKey(Configuration)
    pc_groups = models.ManyToManyField(PCGroup, related_name='pcs', blank=True)
    package_list = models.ForeignKey(PackageList, null=True, blank=True)
    custom_packages = models.ForeignKey(CustomPackages, null=True, blank=True)
    site = models.ForeignKey(Site, related_name='pcs')
    is_active = models.BooleanField(_('active'), default=False)
    is_update_required = models.BooleanField(_('update required'),
                                             default=False)
    # This field is used to communicate to the JobManager on each PC that it
    # should send an update of installed packages next time it contacts us.
    do_send_package_info = models.BooleanField(_('send package info'),
                                                 default=True)
    creation_time = models.DateTimeField(_('creation time'),
        auto_now_add=True)
    last_seen = models.DateTimeField(_('last seen'), null=True, blank=True)

    @property
    def current_packages(self):
        return set(self.package_list.names_of_installed_package)

    @property
    def wanted_packages(self):
        wanted_packages = set(
            self.distribution.package_list.names_of_installed_package
        )

        for group in self.pc_groups.all():
            iis = group.custom_packages.install_infos
            for do_add, name in iis.values_list('do_add', 'package__name'):
                if do_add:
                    wanted_packages.add(name)
                else:
                    wanted_packages.discard(name)

        iis = self.custom_packages.install_infos
        for do_add, name in iis.values_list('do_add', 'package__name'):
            if do_add:
                wanted_packages.add(name)
            else:
                wanted_packages.discard(name)

        return wanted_packages

    @property
    def pending_package_updates(self):
        wanted = self.wanted_packages
        current = self.current_packages
        return (wanted - current, current - wanted)

    @property
    def pending_packages_add(self):
        return self.wanted_packages - self.current_packages

    @property
    def pending_packages_remove(self):
        return self.current_packages - self.wanted_packages

    class Status:
        """This class represents the status of af PC. We may want to do
        something similar for jobs."""

        def __init__(self, state, priority):
            self.state = state
            self.priority = priority

    @property
    def status(self):
        if not self.is_active:
            return self.Status(NEW, INFO)
        elif self.is_update_required:
            # If packages require update
            return self.Status(UPDATE, WARNING)
        else:
            # Get a list of all jobs associated with this PC and see if any of
            # them failed.
            from job.models import Job
            failed_jobs = self.jobs.filter(status=Job.FAILED)
            if len(failed_jobs) > 0:
                # Only UNHANDLED failed jobs, please.
                return self.Status(FAIL, IMPORTANT)
            else:
                return self.Status(OK, None)

    def get_list_of_configurations(self):
        configs = [self.site.configuration]
        configs.extend([g.configuration for g in self.pc_groups.all()])
        configs.append(self.configuration)
        return configs

    def get_config_value(self, key, default=None):
        value = default
        configs = self.get_list_of_configurations()
        for conf in configs:
            try:
                entry = conf.entries.get(key=key)
                value = entry.value
            except ConfigurationEntry.DoesNotExist:
                pass
        return value

    def get_full_config(self):
        result = {}
        configs = self.get_list_of_configurations()
        for conf in configs:
            for entry in conf.entries.all():
                result[entry.key] = entry.value
        return result

    def get_merged_config_list(self, key, default=None):
        result = default[:] if default is not None else []

        configs = [self.site.configuration]
        configs.extend([g.configuration for g in self.pc_groups.all()])
        configs.append(self.configuration)

        for conf in configs:
            try:
                entry = conf.entries.get(key=key)
                for v in entry.value.split(","):
                    v = v.strip()
                    if v != '' and v not in result:
                        result.append(v)
            except ConfigurationEntry.DoesNotExist:
                pass

        return result

    def get_absolute_url(self):
        return reverse('computer', args=(self.site.uid, self.uid))

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
