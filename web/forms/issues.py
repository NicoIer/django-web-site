from django import forms
from web.forms.bootstrap import BootstrapForm
from web.models import Issues


class IssuesModelForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Issues
        exclude = ['project', 'creator']
        # fields = '__all__'

    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        BootstrapForm.__init__(self, *args, **kwargs)
