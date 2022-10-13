from django.urls import path, re_path, include

from web.views import account, project, manage, wiki, file, conf, issues
from web.views import test

manage_urls = [
    path('dashboard/', manage.dashboard, name='dashboard'),

    path('issues/', issues.issues_home, name='issues'),
    # path('issues/create/',issues.create_issue,name='create_isse'),
    
    path('statistics/', manage.dashboard, name='statistics'),

    path('wiki/', wiki.home, name='wiki'),
    path('wiki/add', wiki.add, name='wiki_add'),
    re_path(r'wiki/delete/(?P<wiki_id>\d+)', wiki.delete, name='wiki_delete'),
    re_path(r'wiki/edit/(?P<wiki_id>\d+)', wiki.edit, name='wiki_edit'),
    # ToDo 改变这个上传图片的view的路由
    path('wiki/upload/', wiki.upload_image_url, name='image_upload'),

    path('settings/', conf.home, name='settings'),
    path('settings/delete', conf.delete, name='project_delete'),
    path('settings/ensure_delete', conf.ensure_delete, name='project_ensure_delete')

]

urlpatterns = [
    path('register/', account.register, name='register'),
    path('login/', account.login_view, name='login'),
    path('logout/', account.logout, name='logout'),
    path('send/mail/', account.send_mail, name='send_mail'),
    path('project/', project.project_home, name='project_list'),
    # star/join/id
    re_path(r'project_star/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_star, name='project_star'),
    #
    re_path(r'^manage/(?P<project_id>\d+)/', include(manage_urls)),
    # 文件上传
    re_path(r'file/(?P<project_id>\d+)/', file.file_home, name='file_home'),
    re_path(r'file_delete/(?P<project_id>\d+)/', file.file_delete, name='file_delete'),
    path('get_upload_url/', file.get_upload_url, name='get_upload_url'),
    path(r'get_download_url/', file.get_download_url, name='get_download_url'),
    path(r'file_download/', file.file_download, name='file_download'),
    re_path(r'upload_success/(?P<project_id>\d+)', file.upload_success, name='upload_success'),

    # 测试内容
    path('test/', test.test, name='test'),
    # 获取数据 127.0.0.1：8000/web/get_data
    path('get_data/', test.get_data, name='get_data')
]
