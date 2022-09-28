from web import models
from django import forms

from web.forms.bootstrap import BootstrapForm
from web.models import Project
from web.utils import Tracer


class WikiModelForm(forms.ModelForm, BootstrapForm):
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        BootstrapForm.__init__(self, *args, **kwargs)

    def is_valid(self):
        return super(forms.ModelForm, self).is_valid()

    class Meta:
        model = models.Wiki
        exclude = ['project']

    def save(self, commit=True):
        super().save()
