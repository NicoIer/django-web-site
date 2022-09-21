from django.urls import path
from web.views import account, project
from web.views import test


urlpatterns = [
    path('register/', account.register, name='register'),
    path('login/', account.login_view, name='login'),
    path('logout/',account.logout,name='logout'),
    path('send/mail/', account.send_mail, name='send_mail'),
    path('project/',project.home),

    # 测试内容
    path('test/', test.test, name='test'),
    # 获取数据 127.0.0.1：8000/web/get_data
    path('get_data/', test.get_data, name='get_data')
]
