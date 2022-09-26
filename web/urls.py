from django.urls import path, re_path, include

from web.views import account, project, manage
from web.views import test

urlpatterns = [
    path('register/', account.register, name='register'),
    path('login/', account.login_view, name='login'),
    path('logout/', account.logout, name='logout'),
    path('send/mail/', account.send_mail, name='send_mail'),
    path('project/', project.project_home, name='project_list'),
    # star/join/id
    re_path(r'project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_star, name='project_star'),
    #
    re_path(r'^manage/(?P<project_id>\d+)/', include([
        path('dashboard/', manage.dashboard, name='dashboard'),
        path('issues/', manage.dashboard, name='issues'),
        path('statistics/', manage.dashboard, name='statistics'),
        path('file/', manage.dashboard, name='file'),
        path('wiki/', manage.dashboard, name='wiki')
    ])),
    # 测试内容
    path('test/', test.test, name='test'),
    # 获取数据 127.0.0.1：8000/web/get_data
    path('get_data/', test.get_data, name='get_data')
]
