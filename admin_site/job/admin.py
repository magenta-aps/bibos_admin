
from django.contrib import admin

from models import Script, Batch, Job, Input, Parameter

ar = admin.site.register


class JobInline(admin.TabularInline):
    model = Job


class BatchAdmin(admin.ModelAdmin):
    fields = ['name', 'script', 'targets']
    inlines = [JobInline]


class InputInline(admin.TabularInline):
    model = Input
    extra = 1


class ScriptAdmin(admin.ModelAdmin):
    inlines = [InputInline]

ar(Script, ScriptAdmin)
ar(Batch, BatchAdmin)
ar(Job)
ar(Parameter)

