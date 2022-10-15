from django.contrib.auth.models import AbstractUser
from django.db import models


class Wiki(models.Model):
    # 我是多的一方
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='标题', max_length=32)
    content = models.TextField(verbose_name='内容', blank=True, null=True)
    # 反向查询时用的name 就是 related_name
    parent = models.ForeignKey(verbose_name='夫文章', on_delete=models.CASCADE, to='Wiki', related_name='child',
                               default=None, null=True, blank=True)
    level = models.IntegerField('级别', default=1)

    def __str__(self):
        return self.title


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

    bucket = models.CharField(verbose_name='minIO对象存储桶', max_length=128, default="")
    region = models.CharField(verbose_name='minIO对象存储区域', max_length=32, default="")

    join_count = models.SmallIntegerField(verbose_name='参与人数', default=1)
    creator = models.ForeignKey(to='User', verbose_name='创建者', max_length=32,
                                on_delete=models.CASCADE, related_name='created_project')
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    # 根据哪张表的哪些字段来索引
    # 无法 增加 删除 修改
    # project_user = models.ManyToManyField(to='User', through='ProjectUser', through_fields=('project', 'user'))


# Create your models here.
class User(AbstractUser):
    """
    用户模型
    """
    # 服务等级字段
    # service = models.ForeignKey(verbose_name='服务等级', to='PricePolicy', null=True, blank=True,
    #                             on_delete=models.PROTECT)
    # price_policy = models.ForeignKey(verbose_name='参与者', to='PricePolicy',default=None, on_delete=models.CASCADE)
    # project_num = models.SmallIntegerField(verbose_name='拥有的用户名')
    joined_project = models.ManyToManyField(to='Project', verbose_name='参加的项目', related_name='joined_user')
    stared_project = models.ManyToManyField(to='Project', verbose_name='星标的项目', related_name='stared_user')


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


class FileRepository(models.Model):
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)
    file_type_choices = (
        (1, '文件'),
        (2, '文件夹'),
    )
    file_type = models.SmallIntegerField(verbose_name='类型', choices=file_type_choices)
    name = models.CharField(verbose_name='名称', max_length=128, help_text='文件/文件夹 名称')
    # minio 对应文件对象的key
    key = models.CharField(verbose_name='minio_key', max_length=128, null=True, blank=True)
    etag = models.CharField(verbose_name='ETag', max_length=128, default='')

    file_size = models.IntegerField(verbose_name='文件大小', null=True, blank=True)
    file_path = models.CharField(verbose_name='文件路径', max_length=255, null=True, blank=True)

    parent = models.ForeignKey(verbose_name='父级目录', to='FileRepository', related_name='child',
                               on_delete=models.CASCADE, null=True, blank=True)
    update_user = models.ForeignKey(verbose_name='最近更新者', to='User', null=True, blank=True,
                                    on_delete=models.SET_NULL)
    update_datetime = models.DateTimeField(verbose_name='更新时间', auto_now=True)


class Module(models.Model):
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)
    title = models.CharField('模块名称', max_length=128)

    def __str__(self):
        return self.title


class Issues(models.Model):
    creator = models.ForeignKey(verbose_name='创建者', to='User', on_delete=models.SET_NULL, null=True, blank=True)
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)
    issues_type = models.ForeignKey(verbose_name='问题类型', to='IssuesType', on_delete=models.CASCADE)
    module = models.ForeignKey(verbose_name='模块', to='Module', null=True, blank=True, on_delete=models.CASCADE)
    subject = models.CharField(verbose_name='主题', max_length=80)
    desc = models.TextField(verbose_name='问题描述')
    priority_choices = (
        ('danger', '高'),
        ('warning', '中'),
        ('success', '低')
    )
    priority = models.CharField(verbose_name='优先级', max_length=12, choices=priority_choices, default='danger')

    status_choices = (
        (1, '新建'),
        (2, '处理中'),
        (3, '已解决'),
        (4, '已忽略'),
        (5, '待反馈'),
        (6, '已关闭'),
        (7, '重新打开'),
    )
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices, default=1)
    # 当被指派人被删除后 ... Issues应该被删除么？
    assign = models.ForeignKey(verbose_name='指派', to='User', related_name='task', null=True, blank=True,
                               on_delete=models.CASCADE, default=None)
    attention = models.ManyToManyField(verbose_name='关注者', to='User', related_name='observe')
    start_date = models.DateField(verbose_name='开始时间', null=True, blank=True)
    end_date = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)
    latest_update_date = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    mode_choices = (
        (1, '公开模式'),
        (2, '隐私模式'),
    )
    mode = models.SmallIntegerField(verbose_name='模式', choices=mode_choices, default=1)
    parent = models.ForeignKey(verbose_name='父问题', to='Issues', related_name='child', on_delete=models.SET_NULL,
                               null=True, blank=True, default=None)


class IssuesType(models.Model):
    PROJECT_INIT_LIST = ['task', 'bug', 'function']
    title = models.CharField(verbose_name='类型名称', max_length=128)
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
