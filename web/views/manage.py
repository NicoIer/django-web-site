from django.http import HttpResponse
from django.shortcuts import render, redirect

from web import models
from web.utils import check_login


@check_login
def dashboard(request, project_id: int, *args, **kwargs):
    """
    进去项目管理后台 -> 需要检查用户登录状态 -> 检查project
    :param request:
    :param project_id:
    :param args:
    :param kwargs:
    :return:
    """
    try:
        project = models.Project.objects.get(id=project_id)
    except Exception:
        return redirect('project_list')
    if project in request.tracer.user.joined_project.all() or project in request.tracer.user.created_project.all():
        return render(request, 'web/dashboard.html', locals())
    else:
        return redirect('project_list')
