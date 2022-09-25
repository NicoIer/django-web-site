import datetime

from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect

from web import models
from web.forms.project import ProjectModelForm
from web.models import User


class Tracer(object):
    def __init__(self):
        self.user = None
        self.price_policy = None


def check_login(func):
    def warp(request: HttpRequest, *args, **kwargs):
        if request.session.get('uid', None) or request.COOKIES.get('uid', None):
            uid = request.COOKIES.get('uid')
            request.session['uid'] = uid
            request.session['username'] = request.COOKIES.get('username')
            try:
                # 查询这个user 并存储
                request.tracer.user = User.objects.get(id=uid)
            except Exception:
                return HttpResponseRedirect('/web/login/')

            if request.tracer.user is None:
                return HttpResponseRedirect('/web/login/')
            else:  # 这个用户存在,则允许通过装饰器
                # 顺便更新下用户的状态
                # ToDo 优化这个查询,耗时太长
                transaction = models.Transaction.objects. \
                    filter(user=request.tracer.user, status=2).order_by('-id').first()

                if transaction and transaction.end_datetime < datetime.datetime.now():
                    transaction = models.Transaction.objects. \
                        get(user=request.tracer.user, status=2, price_policy__category=1)
                    request.tracer.price_policy = transaction.price_policy

                return func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/web/login/')

    return warp


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


def update_project_star(request: HttpRequest, project_type: str, project_id: int) -> HttpResponse:
    try:
        project = models.Project.objects.get(id=project_id, creator=request.tracer.user)
    except Exception:
        return HttpResponse("???")
    remove = project.star
    project.star = not project.star
    project.save()

    if project_type == 'my':  #
        if remove:
            request.tracer.user.stared_project.remove(project_id)
        else:
            request.tracer.user.stared_project.add(project_id)
        return redirect('project_list')
    elif project_type == 'join' and project in request.tracer.user.joined_project.all():
        if remove:
            request.tracer.user.stared_project.remove(project_id)
        else:
            request.tracer.user.stared_project.add(project_id)
        return redirect('project_list')
    else:
        return HttpResponse("?????")
