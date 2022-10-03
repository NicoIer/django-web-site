import random
from typing import Optional

import redis
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django_redis import get_redis_connection

from web.forms.bootstrap import BootstrapForm
from web.models import User
from django import forms
from django.conf import settings
from django.core import mail as django_mail


class RegisterModelForm(BootstrapForm, forms.ModelForm):
    email = forms.EmailField(label='邮箱')
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    confirm_password = forms.CharField(label='确认密码', widget=forms.PasswordInput())
    code = forms.CharField(label='验证码')

    class Meta:
        model = User
        # 在前面的先校验
        fields = ('username', 'password', 'confirm_password', 'email', 'code')

    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.user = None
        BootstrapForm.__init__(self, *args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('用户名已存在')
        else:
            return username

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 8:
            raise ValidationError('密码过于简单')
        else:
            return password

    def clean_confirm_password(self):
        confirm_pwd = self.cleaned_data['confirm_password']
        try:  # password或许还没有校验 cleaned_data中还没有password
            password = self.cleaned_data['password']
        except KeyError:
            raise ValidationError('password未校验')

        if confirm_pwd != password:
            raise ValidationError('两次密码不一致')
        else:
            return confirm_pwd

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('邮箱已注册')
        else:
            return email

    def clean_code(self):
        code = self.cleaned_data['code']
        try:  #
            email = self.cleaned_data['email']
        except KeyError:
            return code
        # 获取连接
        conn = get_redis_connection('REDIS')
        redis_code: bytes = conn.get(email)
        # 立即删除key
        conn.delete(email)
        if not redis_code:
            raise ValidationError('验证码未发送')
        elif redis_code.decode('utf-8') != code.strip():
            raise ValidationError('验证码错误')
        else:
            return code

    def save(self, commit=True) -> Optional[User or None]:
        username, email, password = self.cleaned_data['username'], self.cleaned_data['email'], self.cleaned_data[
            'password']
        try:
            self.user = self.Meta.model.objects.create_user(username, email, password)
        except Exception:
            # 并行插入时 可能会有错误
            self.add_error('username', ValidationError('用户名已存在'))
            return None
        else:
            return self.user


class LoginForm(BootstrapForm, forms.Form):
    # 校验的顺序按照这里书写的顺序来
    username = forms.CharField(label='用户名', max_length=150)
    password = forms.CharField(label='密码', widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        BootstrapForm.__init__(self, *args, **kwargs)
        self.user: Optional[User, None] = None

    def clean_password(self):
        password = self.cleaned_data.get('password', None)
        username = self.cleaned_data.get('username', None)
        if username is None:  # 用户名有误,轮不到password报错
            return password
        else:
            self.user = authenticate(username=username, password=password)
            if self.user is None:
                raise ValidationError('密码错误')
            else:
                return password

    def clean_username(self):
        username = self.cleaned_data.get('username', None)
        if not username:
            raise ValidationError('用户名格式有误')
        else:
            if User.objects.filter(username=username):
                return username
            else:
                raise ValidationError('用户名不存在')


# ToDo 网易邮箱gg了 需要重新弄
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
        if self.send_mail(email, self.state) != 1:
            raise ValidationError('验证码发送失败~~')
        return email

    @staticmethod
    def send_mail(email, state: str) -> int:
        # 在此发送邮件
        # 我的评价,在这里做邮件发送不好,耦合了
        code = random.randrange(1000, 9999)
        print(code)
        conn: redis.Redis = get_redis_connection('REDIS')
        if conn.set(email, code, ex=300, nx=True):
            return django_mail.send_mail(
                subject=f'User {state}',
                from_email=settings.EMAIL_HOST_USER,
                message=f'您的验证码{code}',
                recipient_list=(email,)
            )
        else:
            # self.fields['email'].widgets.attrs['data-content'] = '验证码已发送'
            # print('已经发送过了')
            raise ValidationError('验证码已经发送')
