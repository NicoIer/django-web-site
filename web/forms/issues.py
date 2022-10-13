from django import forms
from web.forms.bootstrap import BootstrapForm
from web.models import Issues


class IssuesModelForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Issues
        exclude = ['project', 'creator', ]
        # fields = '__all__'
        widgets = {
            'assign': forms.Select(attrs={'class': 'selectpicker'}),
            'attention': forms.SelectMultiple(attrs={
                'class': 'selectpicker',
                'data-live-search': 'true',
                'data-action-box': 'true',
            })
        }

    def __init__(self, *args, **kwargs):
        select_set = {'assign', 'priority'}
        forms.ModelForm.__init__(self, *args, **kwargs)
        BootstrapForm.__init__(self, select_set=select_set)
        # self.fields['parent'].required = False
