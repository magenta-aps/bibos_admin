import datetime

from django import forms
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User

from models import Site, PCGroup, ConfigurationEntry, PC
from job.models import Script, Input


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
    # Need to set up this side of the many-to-many relation between groups
    # and PCs manually.
    pcs = forms.ModelMultipleChoiceField(
        queryset=PC.objects.all(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            initial = kwargs.setdefault('initial', {})
            initial['pcs'] = [pc.pk for pc in
                              kwargs['instance'].pcs.all()]

        forms.ModelForm.__init__(self, *args, **kwargs)        

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, False)

        old_save_m2m = self.save_m2m
        def save_m2m():
            old_save_m2m()
            instance.pcs.clear()
            for pc in self.cleaned_data['pcs']:
                instance.pcs.add(pc)

        self.save_m2m = save_m2m

        # Do we need to save all changes now?
        if commit:
            instance.save()
            self.save_m2m()

        return instance

    class Meta:
        model = PCGroup
        exclude = ['site', 'configuration', 'custom_packages']


class ScriptForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ScriptForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['site'].widget.attrs['readonly'] = True

    class Meta:
        model = Script


class ConfigurationEntryForm(forms.ModelForm):
    class Meta:
        model = ConfigurationEntry
        exclude = ['owner_configuration']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ('groups', 'user_permissions', 'first_name', 'last_name',
                   'is_staff', 'is_active', 'is_superuser', 'date_joined')


class ParameterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        script = kwargs.pop('script')
        super(ParameterForm, self).__init__(*args, **kwargs)

        for i, inp in enumerate(script.inputs.all().order_by('position')):
            name = 'parameter_%s' % i
            field_data = {
                'label': "Parameter %s" % (i + 1),
                'required': True if inp.mandatory else False
            }
            if inp.value_type == Input.FILE:
                self.fields[name] = forms.FileField(**field_data)
            elif inp.value_type == Input.DATE:
                field_data['initial'] = datetime.datetime.now
                field_data['widget'] = forms.DateTimeInput(
                    attrs={'class': 'dateinput'}
                )
                self.fields[name] = forms.DateTimeField(**field_data)
            else:
                self.fields[name] = forms.CharField(**field_data)


class PCForm(forms.ModelForm):
    class Meta:
        model = PC
        exclude = ('uid', 'configuration', 'package_list', 'site',
                   'is_update_required', 'creation_time', 'last_seen',
                   'custom_packages')
