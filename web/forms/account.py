from web.models import User
from django import forms


class RegisterModelForm(forms.ModelForm):
    email = forms.EmailField(label='邮箱')
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    confirm_password = forms.CharField(label='确认密码', widget=forms.PasswordInput())
    code = forms.CharField(label='验证码')

    class Meta:
        model = User
        fields = ('username', 'password', 'confirm_password', 'email', 'code')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # name是变量名 , field.label是传参的label
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = f'{name}'
