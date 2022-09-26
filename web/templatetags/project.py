from django.db.models import QuerySet
from django.template import Library

from web.utils import check_login

register = Library()


@check_login
@register.inclusion_tag('inclusion_tag/project_home_drop_menu.html')
def project_drop_menu(request):
    joined_projects = request.tracer.user.joined_project.all()
    created_projects = request.tracer.user.project_set.all()
    # 查询我创建的所有项目
    # 查询我参与的所有项目
    return locals()


@check_login
@register.inclusion_tag('inclusion_tag/project_home_panel.html')
def project_panel(projects: QuerySet, panel_name: str, project_type: str = ""):
    print(project_type)
    return locals()
