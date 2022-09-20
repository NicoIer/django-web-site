from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    """
    用户模型
    """
    # 暂时不需要任何额外字段(phone等字段)
    pass


class PricePolicy(models.Model):
    """
    价格策略
    """
    category_choices = (
        (1, '免费版'),
        (2, '收费版'),
        (3, '其他')
    )

    category = models.SmallIntegerField(verbose_name='收费类型', default=2, choices=category_choices)
    title = models.CharField(verbose_name='标题', max_length=32)
    # PositiveIntegerField -> 正整数类型
    price = models.PositiveIntegerField(verbose_name='价格')
    project_num = models.PositiveIntegerField(verbose_name='项目数')
    project_member_num = models.PositiveIntegerField(verbose_name='项目成员数')
    project_space = models.PositiveIntegerField(verbose_name='单项目空间')
    per_file_size = models.PositiveIntegerField(verbose_name='单文件大小')
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


class Transaction(models.Model):
    """
    交易记录
    """
    status_choice = (
        (1, '已支付'),
        (2, '未支付')
    )

    status = models.SmallIntegerField(verbose_name='支付状态', choices=status_choice)
    order = models.CharField(verbose_name='订单号', max_length=64, unique=True)

    user = models.ForeignKey(verbose_name='用户', to='User', on_delete=models.CASCADE)
    price_policy = models.ForeignKey(verbose_name='价格策略', to='PricePolicy', on_delete=models.CASCADE)

    count = models.IntegerField(verbose_name='数量', help_text='0表示永久')
    price = models.IntegerField(verbose_name='实际支付价格')

    start_datetime = models.DateTimeField(verbose_name='开始时间', null=True, blank=True)
    end_datetime = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)

    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


class Project(models.Model):
    """
    项目表
    """
    COLOR_CHOICE = (
        (1, '#56b8eb'),
        (2, '#f28033'),
        (3, '#ebc656'),
        (4, '#a2d148'),
        (5, '#20bfa4'),
        (6, '#7461c2'),
        (7, '#20bfa3')
    )
    name = models.CharField(verbose_name='项目名', max_length=32)
    color = models.SmallIntegerField(verbose_name='颜色', choices=COLOR_CHOICE, default=1)
    desc = models.CharField(verbose_name='项目描述', max_length=255, null=True, blank=True)
    star = models.BooleanField(verbose_name='星标', default=False)

    bucket = models.CharField(verbose_name='minIO对象存储桶', max_length=128)
    region = models.CharField(verbose_name='minIO对象存储区域', max_length=32)

    join_count = models.SmallIntegerField(verbose_name='参与人数')
    creator = models.CharField(verbose_name='创建者', max_length=32)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


class ProjectUser(models.Model):
    """
    项目参与者
    """

    user = models.ForeignKey(verbose_name='参与者', to='User', on_delete=models.CASCADE, related_name='user')
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)

    star = models.BooleanField(verbose_name='星标', default=False)
    inviter = models.ForeignKey(verbose_name='邀请者', to='User', on_delete=models.CASCADE, related_name='inviter')
    create_datetime = models.DateTimeField(verbose_name='加入时间', auto_now_add=True)
