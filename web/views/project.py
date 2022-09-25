from django.http import HttpResponse
from django.shortcuts import render, redirect

from web import models
from web.forms.project import ProjectModelForm
from web.utils import check_login, check_form


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
    if project_type == 'my':
        try:
            project = models.Project.objects.get(id=project_id, creator=request.tracer.user)
        except Exception:
            # ToDo 对于异常的星标请求 需要做详细的额外处理
            return HttpResponse("????")
        if not project.star:  # 没有star才 star
            project.star = True
            project.save()
            request.tracer.user.stared_project.add(project_id)

            return redirect('project_list')
        else:
            return HttpResponse("????")
    elif project_type == 'join':
        try:
            # 项目存在不存在
            project = models.Project.objects.get(id=project_id)
            # 且用户已经加入该项目
        except Exception:
            return HttpResponse("????")
        if project in request.tracer.user.joined_project.all():
            # 则将该项目添加到用户的星标列表
            if project not in request.tracer.user.stared_project.all():
                request.tracer.user.stared_project.add(project_id)

                return redirect('project_list')
            else:
                return HttpResponse("????")
        else:
            return HttpResponse("????")

    else:
        return HttpResponse(status=404)


@check_login
def project_cancel_star(request, project_type: str, project_id: int):
    if project_type == 'my':
        try:
            project = models.Project.objects.get(id=project_id, creator=request.tracer.user)
        except Exception:
            # ToDo 对于异常的星标请求 需要做详细的额外处理
            return HttpResponse("????")
        if project.star:
            project.star = False
            project.save()
            request.tracer.user.stared_project.remove(project_id)
            return redirect('project_list')
        else:
            return HttpResponse("????")
    elif project_type == 'join':
        try:
            # 项目存在不存在
            project = models.Project.objects.get(id=project_id)
            # 且用户已经加入该项目
        except Exception:
            return HttpResponse("????")
        if project in request.tracer.user.joined_project.all():
            # 则将该项目从用户的星标列表移除
            request.tracer.user.stared_project.remove(project_id)
            return redirect('project_list')
        else:
            return HttpResponse("????")
    else:

        return HttpResponse(status=404)
