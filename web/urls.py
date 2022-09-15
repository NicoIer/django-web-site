from django.contrib import admin
from django.template.defaulttags import url
from django.urls import path, include

from web.views import account

urlpatterns = [
    path('register/', account.register, name='register'),
    path('send/mail/', account.send_mail, name='send_mail'),
]
