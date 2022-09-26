from web import models
from django import forms

from web.forms.bootstrap import BootstrapForm
from web.models import Project
from web.utils import Tracer


class WikiModelForm(forms.ModelForm, BootstrapForm):
    class Meta:
        model = models.Wiki
        exclude = ['project', 'parent']

    def save(self, commit=True):
        super().save()
