
from django.contrib import admin

from models import Configuration, ConfigurationEntry, PackageList, Package
from models import Site, Distribution, PCGroup, PC, CustomPackages
from models import PackageInstallInfo, PackageStatus
# Job-related stuff
from models import Script, Batch, Job, Input, Parameter
ar = admin.site.register


class PackageInstallInfoInline(admin.TabularInline):
    model = PackageInstallInfo
    extra = 3


class PackageStatusInline(admin.TabularInline):
    model = PackageStatus
    extra = 3


class ConfigurationEntryInline(admin.TabularInline):
    model = ConfigurationEntry
    extra = 3


class PackageListAdmin(admin.ModelAdmin):
    inlines = [PackageStatusInline]


class CustomPackagesAdmin(admin.ModelAdmin):
    inlines = [PackageInstallInfoInline]


class ConfigurationAdmin(admin.ModelAdmin):
    fields = ['name']
    inlines = [ConfigurationEntryInline]


class PCInline(admin.TabularInline):
    model = PC.pc_groups.through
    extra = 3


class PCGroupAdmin(admin.ModelAdmin):
    inlines = [PCInline]


class JobInline(admin.TabularInline):
    fields = ['pc']
    model = Job
    extra = 1


class ParameterInline(admin.TabularInline):
    model = Parameter
    extra = 1


class BatchAdmin(admin.ModelAdmin):
    fields = ['site', 'name', 'script']
    inlines = [JobInline, ParameterInline]


class InputInline(admin.TabularInline):
    model = Input
    extra = 1


class ScriptAdmin(admin.ModelAdmin):
    inlines = [InputInline]


ar(Configuration, ConfigurationAdmin)
ar(PackageList)
ar(CustomPackages, CustomPackagesAdmin)
ar(Site)
ar(Distribution)
ar(PCGroup, PCGroupAdmin)
ar(PC)
ar(Package)
# Job related stuff
ar(Script, ScriptAdmin)
ar(Batch, BatchAdmin)
ar(Job)
ar(Parameter)
