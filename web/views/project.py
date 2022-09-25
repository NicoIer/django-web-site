from django.shortcuts import render

from web import models
from web.decorators import check_login
from web.forms.project import ProjectModelForm
from web.models import User, Project
from django.http import JsonResponse, HttpRequest


@check_login
def project_home(request):
    """
    :param request:
    :return:
    """
    if request.method == 'GET':

        star_projects = []
        join_projects = []
        create_projects = []
        # 当前用户创建的项目
        for create in request.tracer.user.project_set.all():
            if create.star:
                star_projects.append(create)
            else:
                create_projects.append(create)
        # 当前用户加入的项目
        for join in request.tracer.user.joined_project.all():
            if join.star:
                star_projects.append(join)
            else:
                join_projects.append(join)

        # check logging后 tracer必定是User
        user = request.tracer.user
        form = ProjectModelForm()
        return render(request, r'web\project_home.html', locals())
    elif request.method == 'POST':
        form = ProjectModelForm(tracer=request.tracer, data=request.POST)
        return check_form(form, request)


def check_form(form: ProjectModelForm, request: HttpRequest) -> JsonResponse:
    if form.is_valid():
        # 验证通过
        form.instance.creator = request.tracer.user
        # 保存数据到数据库
        form.save()
        #
        return_data = {
            'status': True,
            'error': form.errors
        }
        return JsonResponse(return_data)
    else:
        return_data = {
            'status': False,
            'error': form.errors
        }
        return JsonResponse(data=return_data)
