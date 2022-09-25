from django.template import Library

from web.utils import check_login

register = Library()


@check_login
@register.inclusion_tag('inclusion_tag/all_project_list.html')
def all_project_list(request):
    joined_projects = request.tracer.user.joined_project.all()
    created_projects = request.tracer.user.project_set.all()
    # 查询我创建的所有项目
    # 查询我参与的所有项目
    return locals()
