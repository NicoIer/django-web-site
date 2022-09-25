from django.http import HttpResponse
from django.shortcuts import render, redirect

from web import models
from web.forms.project import ProjectModelForm
from web.utils import check_login, check_form, update_project_star


@check_login
def project_home(request):
    """
    :param request:
    :return:
    """
    if request.method == 'GET':

        # 当前用户星标的项目
        star_projects = request.tracer.user.stared_project.all()
        # 当前用户创建但未被星标的项目
        create_projects = []
        for create in request.tracer.user.project_set.all():
            if not create.star:
                create_projects.append(create)
        # 当前用户加入的但没有被自己星标的项目
        join_projects = [project for project in request.tracer.user.joined_project.all()
                         if project not in star_projects]

        # check logging后 tracer必定是User
        user = request.tracer.user
        form = ProjectModelForm()
        return render(request, r'web\project_home.html', locals())
    elif request.method == 'POST':
        form = ProjectModelForm(tracer=request.tracer, data=request.POST)
        return check_form(form, request)


@check_login
def project_star(request, project_type: str, project_id: int):
    return update_project_star(request, project_type, project_id)
