from web import models
from django import forms
from web.forms.bootstrap import BootstrapForm


# ToDo 所有的form都有一个问题 get 和 post 时的 __init__ 不需要一样  优化它
class WikiModelForm(forms.ModelForm, BootstrapForm):
    def __init__(self, method="get", project=None, parent=None, *args, **kwargs):
        # super调用 学到了没
        forms.ModelForm.__init__(self, *args, **kwargs)
        # BootstrapForm 并没有fields字段 实际上是从self的父类中找到的fields
        BootstrapForm.__init__(self, *args, **kwargs)
        #
        self.instance.project = project
        self.instance.parent = parent
        #
        if method == 'get':
            parent_wikis = [("", 'NULL')]
            parent_wikis.extend(list(models.Wiki.objects.filter(project=project).values_list('id', 'title')))
            self.fields['parent'].choices = parent_wikis

    def is_valid(self):
        return super(forms.ModelForm, self).is_valid()

    class Meta:
        model = models.Wiki
        exclude = ['project']

    def save(self, commit=True):
        super(forms.ModelForm, self).save()
