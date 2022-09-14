from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    # 暂时不需要任何额外字段(phone等字段)
    pass
