from typing import Optional

from django import forms
from django.core.exceptions import ValidationError

from web import models
from web.bootstrap import BootstrapForm
from web.models import User


class ProjectModelForm(BootstrapForm, forms.ModelForm):
    def __init__(self, tracer=None, *args, **kwargs):
        super(ProjectModelForm, self).__init__(*args, **kwargs)
        self.tracer = tracer

    class Meta:
        model = models.Project
        # 重写desc字段为
        fields = ['name', 'color', 'desc']
        widgets = {
            'desc': forms.Textarea
        }

    # desc = forms.CharField(widget=forms.Textarea)
    def clean_name(self):
        # 用户创建的pro是否重名
        name = self.cleaned_data['name']
        print(self.tracer.price_policy.project_num)
        if self.tracer and models.Project.objects.filter(name=name, creator=self.tracer.user).exists():
            raise ValidationError('项目名已存在')
        else:
            return name
        # 没有能够完成num操作
