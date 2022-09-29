from django.db.models import QuerySet

from web import models
from django import forms

from web.forms.bootstrap import BootstrapForm
from web.models import Project
from web.utils import Tracer


class WikiModelForm(forms.ModelForm, BootstrapForm):
    def __init__(self, project=None, parent=None, *args, **kwargs):
        # super调用 学到了没
        forms.ModelForm.__init__(self, *args, **kwargs)
        # BootstrapForm 并没有fields字段 实际上是从self的父类中找到的fields
        BootstrapForm.__init__(self, *args, **kwargs)
        #
        self.instance.project = project
        self.instance.parent = parent
        #
        projects = [("", 'NULL')]
        projects.extend(list(models.Wiki.objects.filter(project=project).values_list('id', 'title')))
        self.fields['parent'].choices = projects

    def is_valid(self):
        return super(forms.ModelForm, self).is_valid()

    class Meta:
        model = models.Wiki
        exclude = ['project']

    def save(self, commit=True):
        super(forms.ModelForm, self).save()
