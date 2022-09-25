from django import forms
from django.core.exceptions import ValidationError

from web import models
from web.forms.bootstrap import BootstrapForm


class ProjectModelForm(BootstrapForm, forms.ModelForm):
    def __init__(self, tracer=None, *args, **kwargs):
        except_set = {'color'}
        super(ProjectModelForm, self).__init__(except_set, *args, **kwargs)
        self.tracer = tracer

        self.fields['color'].widget.attrs['data-toggle'] = 'color-radio'

    class Meta:
        model = models.Project
        # 重写desc字段为
        fields = ['name', 'color', 'desc']
        # 修改其展示方式
        widgets = {
            'desc': forms.Textarea,
            'color': forms.RadioSelect,
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
