
from django.contrib import admin

from models import Script, Batch, Job, Input, Parameter

ar = admin.site.register

ar(Script)
ar(Batch)
ar(Job)
ar(Input)
ar(Parameter)

