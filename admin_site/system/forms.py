import datetime

from django import forms
from django.contrib.auth.models import User

from models import Site, PCGroup, ConfigurationEntry, PC
from models import Script, Input, SecurityProblem
from account.models import UserProfile

from django.utils.translation import ugettext as _


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
        if 'instance' in kwargs and kwargs['instance'] is not None:
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
        fields = '__all__'


class ConfigurationEntryForm(forms.ModelForm):
    class Meta:
        model = ConfigurationEntry
        exclude = ['owner_configuration']


class UserForm(forms.ModelForm):
    usertype = forms.ChoiceField(
        required=True,
        choices=UserProfile.type_choices
    )

    new_password = forms.CharField(
        label=_("Password"), widget=forms.PasswordInput(
            attrs={'class': 'passwordinput'}
        ),
        required=False
    )

    password_confirm = forms.CharField(
        label=_("Password (again)"), widget=forms.PasswordInput(
            attrs={'class': 'passwordinput'}
        ),
        required=False
    )

    initial_type = None

    def __init__(self, *args, **kwargs):
        initial = kwargs.setdefault('initial', {})
        if 'instance' in kwargs and kwargs['instance'] is not None:
            initial['usertype'] = kwargs['instance'].bibos_profile.type
        else:
            initial['usertype'] = UserProfile.SITE_USER
        self.initial_type = initial['usertype']
        forms.ModelForm.__init__(self, *args, **kwargs)

    class Meta:
        model = User
        exclude = ('groups', 'user_permissions', 'first_name', 'last_name',
                   'is_staff', 'is_active', 'is_superuser', 'date_joined',
                   'last_login', 'password')

    def set_usertype_single_choice(self, choice_type):
        self.fields['usertype'].choices = [
            (c, l) for c, l in UserProfile.type_choices if c == choice_type
        ]
        self.fields['usertype'].widget.attrs['readonly'] = True

    # Sets the choices in the usertype widget depending on the usertype
    # of the user currently filling out the form
    def setup_usertype_choices(self, loginuser_type):
        print "Usertype: ", loginuser_type
        if loginuser_type == UserProfile.SUPER_ADMIN:
            # Superadmins can edit everything
            self.fields['usertype'].choices = UserProfile.type_choices
        elif loginuser_type == UserProfile.SITE_ADMIN:
            # If initial type is super_admin, hardcode to that single choice
            if self.initial_type == UserProfile.SUPER_ADMIN:
                self.set_usertype_single_choice(UserProfile.SITE_ADMIN)
                self.fields['usertype'].widget.attrs['readonly']
            else:
                # Only select between site-admins and site users
                self.fields['usertype'].choices = UserProfile.NON_ADMIN_CHOICES
        else:
            # Set to read-only single choice
            self.set_usertype_single_choice(self.initial_type)
            self.fields['usertype'].widget.attrs['readonly']

    def clean(self):
        cleaned_data = self.cleaned_data
        pw1 = cleaned_data.get("new_password")
        pw2 = cleaned_data.get("password_confirm")
        if pw1 != pw2:
            raise forms.ValidationError(_('Passwords must be identical.'))
        return cleaned_data

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        if self.cleaned_data["new_password"]:
            user.set_password(self.cleaned_data["new_password"])
        if commit:
            user.save()
        return user


class ParameterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        script = kwargs.pop('script')
        super(ParameterForm, self).__init__(*args, **kwargs)

        for i, inp in enumerate(script.inputs.all().order_by('position')):
            name = 'parameter_%s' % i
            field_data = {
                'label': inp.name,
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
                   'custom_packages', 'do_send_package_info')


class SecurityProblemForm(forms.ModelForm):
    class Meta:
        model = SecurityProblem
        fields = '__all__'
