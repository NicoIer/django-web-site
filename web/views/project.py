from django.conf import settings
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render, redirect

from web import models
from web.forms.project import ProjectModelForm
from web.utils import check_login, minio_manager


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
        for create in request.tracer.user.created_project.all():
            if not create.star:
                create_projects.append(create)
        # 当前用户加入的但没有被自己星标的项目
        join_projects = [project for project in request.tracer.user.joined_project.all()
                         if project not in star_projects]

        # check logging后 tracer必定是User
        user = request.tracer.user
        form = ProjectModelForm()
        return render(request, 'web/project_home.html', locals())
    elif request.method == 'POST':
        form = ProjectModelForm(tracer=request.tracer, data=request.POST)
        return check_project_form(form, request)


@check_login
def project_star(request, project_type: str, project_id: int):
    return update_project_star(request, project_type, project_id)


def test(request, project_id, *args, **kwargs):
    return HttpResponse('cddcd')


def check_project_form(form: ProjectModelForm, request: HttpRequest) -> JsonResponse:
    if form.is_valid():
        # ToDo 这里可能会有异常 为项目创建一个Bucket
        _ = models.Project.objects.last()
        _id = _.id + 1 if _ else 1
        # toDo 这里可能会有并发异常...
        bucket_name = '{}-{}'.format(request.tracer.user.id, (_id + 1))
        location = settings.MINIO_DEFAULT_REGION

        # 创建桶 顺便改变逻辑
        minio_manager.create_bucket(bucket_name, location)
        minio_manager.set_bucket_public_read(bucket_name)
        # 为项目属性赋值
        form.instance.bucket = bucket_name
        form.instance.region = location

        # 验证通过
        form.instance.creator = request.tracer.user
        # 为项目添加默认ISSUE_TYPE
        issues = []
        for ISSUE_TYPE in models.IssuesType.PROJECT_INIT_LIST:
            issues.append(models.IssuesType(project=form.instance, title=ISSUE_TYPE))
        models.IssuesType.objects.bulk_create(issues)  # 批量添加

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


def update_project_star(request: HttpRequest, project_type: str, project_id: int) -> HttpResponse:
    try:
        project = models.Project.objects.get(id=project_id, creator=request.tracer.user)
    except Exception:
        return HttpResponse("???")
    remove = project.star
    project.star = not project.star
    project.save()

    if project_type == 'my' or project_type == 'star' or (
            project_type == 'join' and project in request.tracer.user.joined_project.all()):  #
        if remove:
            request.tracer.user.stared_project.remove(project_id)
        else:
            request.tracer.user.stared_project.add(project_id)

        return redirect('project_list')
    else:
        return HttpResponse("?????")
