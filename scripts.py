import os, django, sys
from pathlib import Path
import os

# 将对应目录添加到sys.path后,即可以从添加的位置为起始位置导包


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learning_site.settings')
django.setup()
try:
    from web import models
except ImportError:
    exit(0)


def create_policy():
    """"""
    manager = models.PricePolicy.objects
    manager.create(category=1, title='个人免费版', price=0, project_num=3, project_member_num=5, project_space=20,
                   per_file_size=5)
    print('success')


if __name__ == '__main__':
    create_policy()
