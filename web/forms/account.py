import random

import redis
from django.core.exceptions import ValidationError
from django_redis import get_redis_connection

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
            if name == 'email':
                field.widget.attrs['data-toggle'] = 'popover'
                field.widget.attrs['data-content'] = '邮箱格式错误'
                field.widget.attrs['data-placement'] = 'bottom'
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = f'{name}'
            field.required = True


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

    def send_mail(self, email) -> int:
        # 在此发送邮件
        # 我的评价,在这里做邮件发送不好,耦合了
        code = random.randrange(1000, 9999)
        conn: redis.Redis = get_redis_connection('REDIS')
        if conn.set(email, code, ex=360, nx=True):
            return django_mail.send_mail(
                subject='用户注册',
                from_email=settings.EMAIL_HOST_USER,
                message=f'您的验证码{code}',
                recipient_list=(email,)
            )
        else:
            # self.fields['email'].widgets.attrs['data-content'] = '验证码已发送'
            # print('已经发送过了')
            raise ValidationError('验证码已经发送')
