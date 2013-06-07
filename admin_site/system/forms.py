
from django import forms
from django.forms.models import inlineformset_factory

from models import Site, PCGroup
from job.models import Script


class SiteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SiteForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['uid'].widget.attrs['readonly'] = True

    class Meta:
        model = Site
        exclude = ['configuration']


class GroupForm(forms.ModelForm):
    class Meta:
        model = PCGroup
        exclude = ['site', 'configuration', 'package_list']


class ScriptForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ScriptForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['site'].widget.attrs['readonly'] = True

    class Meta:
        model = Script
