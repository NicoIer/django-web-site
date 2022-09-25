from django.db.models import QuerySet
from django.shortcuts import render, redirect

from web import models
from web.utils import check_login, check_form
from web.forms.project import ProjectModelForm
from web.models import User, Project
from django.http import JsonResponse, HttpRequest, HttpResponseRedirect, HttpResponse


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
        join_projects = [project for project in request.tracer.user.joined_project.all() \
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
    print(f'type:{project_type}  project_id:{project_id}')
    if project_type == 'my':
        try:
            project = models.Project.objects.get(id=project_id, creator=request.tracer.user)
            project.update(star=True)
            request.tracer.user.stared_project.add(project_id)
        except Exception:
            # ToDo 对于异常的星标请求 需要做详细的额外处理
            return HttpResponse("????")
        else:
            return redirect('project_list')
    elif project_type == 'join':
        try:
            # 项目存在不存在
            project = models.Project.objects.get(id=project_id)
            # 且用户已经加入该项目
        except Exception:
            return HttpResponse("????")
        else:
            if project in request.tracer.user.joined_project.all():
                # 则将该项目添加到用户的星标列表
                request.tracer.user.stared_project.add(project_id)
                return redirect('project_list')
            else:
                return HttpResponse("????")

    else:
        return HttpResponse(status=404)
