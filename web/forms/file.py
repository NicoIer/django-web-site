from django import forms

from web import models
from web.forms.bootstrap import BootstrapForm


class FileFoldModelForm(forms.ModelForm, BootstrapForm):
    class Meta:
        model = models.FileRepository
        fields = ['name']

    def __init__(self, project=None, parent_id=None, *arg, **kwargs):
        forms.ModelForm.__init__(self, *arg, **kwargs)

        BootstrapForm.__init__(self, *arg, **kwargs)
        self.project = project
        self.parent_id = parent_id

    def clean_name(self):
        name = self.cleaned_data['name']
        # 判断 文件夹是否存在
        if self.parent_id:
            dir_files = models.FileRepository.objects.filter(file_type=2, name=name,
                                                             project=self.project, parent_id=self.parent_id)
        else:
            dir_files = models.FileRepository.objects.filter(file_type=2, name=name,
                                                             project=self.project, parent__isnull=True)

        if dir_files.exists():
            self.add_error('name', 'the folder name already exist')
        else:
            return name

    def is_valid(self):
        return super(forms.ModelForm, self).is_valid()

    def save(self, commit=True):
        return super(forms.ModelForm, self).save()
