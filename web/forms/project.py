from django import forms
from django.core.exceptions import ValidationError

from web import models
from web.bootstrap import BootstrapForm


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
        if self.tracer and models.Project.objects.filter(name=name, creator=self.tracer.user).exists():
            raise ValidationError('项目名已存在')
        else:
            return name
        # 没有能够完成num操作

    def save(self, commit=True):
        super().save()
        # 创建 和 加入是有区别的
        # self.tracer.user.joined_project.add(self.instance)
        self.tracer.user.save()
