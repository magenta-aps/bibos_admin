
from django.contrib import admin

from models import Configuration, ConfigurationEntry, PackageList, Package
from models import Site, Distribution, PCGroup, PC

ar = admin.site.register


class ConfigurationEntryInline(admin.TabularInline):
    model = ConfigurationEntry
    extra = 3


class ConfigurationAdmin(admin.ModelAdmin):
    fields = ['name']
    inlines = [ConfigurationEntryInline]


class PCInline(admin.TabularInline):
    model = PC.pc_groups.through
    extra = 3


class PCGroupAdmin(admin.ModelAdmin):
    inlines = [PCInline]


ar(Configuration, ConfigurationAdmin)
ar(PackageList)
ar(Site)
ar(Distribution)
ar(PCGroup, PCGroupAdmin)
ar(PC)
ar(Package)
