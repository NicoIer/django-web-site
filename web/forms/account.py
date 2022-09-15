import random

from django.core.exceptions import ValidationError

from web.models import User
from django import forms
from django.conf import settings
from django.core import mail as django_mail


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


class EmailForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)
        self.state = self.data.get('state', None)

    email = forms.EmailField(label='email')

    def clean_email(self):
        email = self.cleaned_data['email']
        if self.state not in settings.USER_STATE:
            raise ValidationError('user state error')

        if User.objects.filter(email=email).exists():
            raise ValidationError('email already exists')
        if self.send_mail(email) != 1:
            raise ValidationError('验证码发送失败~~')
        return email

    @staticmethod
    def send_mail(email) -> int:
        # 在此发送邮件
        code = random.randrange(1000, 9999)
        return django_mail.send_mail(
            subject='用户注册',
            from_email=settings.EMAIL_HOST_USER,
            message=f'您的验证码{code}',
            recipient_list=(email,)
        )
