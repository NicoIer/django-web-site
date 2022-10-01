from django.forms import ModelChoiceField

from web import models
from django import forms
from web.forms.bootstrap import BootstrapForm


# ToDo 所有的form都有一个问题 get 和 post 时的 __init__ 不需要一样  优化它
class WikiModelForm(forms.ModelForm, BootstrapForm):
    def __init__(self, project, method, *args, **kwargs):
        # super调用 学到了没
        forms.ModelForm.__init__(self, *args, **kwargs)

        if method == 'get':
            if self.instance.id:
                choices = models.Wiki.objects.filter(project=project). \
                    exclude(id=self.instance.id).values_list('id', 'title')
            else:
                choices = models.Wiki.objects.filter(project=project).values_list('id', 'title')
            self.fields['parent'].choices = choices
        elif method == 'post':
            self.instance.project = project
            self.fields['parent'].required = False

        # BootstrapForm 并没有fields字段 实际上是从self的父类中找到的fields
        BootstrapForm.__init__(self, *args, **kwargs)

    class Meta:
        model = models.Wiki
        exclude = ['project', 'level']

    def save(self, commit=True):
        if self.instance.parent and self.instance.parent != self.instance:
            self.instance.level = self.instance.parent.level + 1
        super(forms.ModelForm, self).save()
