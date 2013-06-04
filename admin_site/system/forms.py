
from django import forms

from models import Site


class SiteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SiteForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['uid'].widget.attrs['readonly'] = True

    class Meta:
        model = Site
        exclude = ['configuration']
