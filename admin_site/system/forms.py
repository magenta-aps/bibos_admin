
from django import forms

from models import Site

class SiteCreateForm(forms.ModelForm):
    class Meta:
        model = Site
        exclude = ['configuration']
