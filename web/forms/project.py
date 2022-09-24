from django import forms

from web import models
from web.bootstrap import BootstrapForm


class ProjectModelForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = models.Project
        # 重写desc字段为
        fields = ['name', 'color', 'desc']
        widgets = {
            'desc': forms.Textarea
        }

    # desc = forms.CharField(widget=forms.Textarea)
