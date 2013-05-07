
from django.contrib import admin

from models import Configuration, ConfigurationEntry, PackageList, Package
from models import Site, Distribution, PCGroup, PC

ar = admin.site.register

ar(Configuration)
ar(ConfigurationEntry)
ar(PackageList)
ar(Site)
ar(Distribution)
ar(Package)
ar(PCGroup)
ar(PC)
