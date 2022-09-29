from django.db.models import QuerySet
from django.template import Library
from django.urls import reverse
from web.utils import check_login

register = Library()


@register.inclusion_tag('inclusion_tag/project_home_drop_menu.html')
def project_drop_menu(request):
    joined_projects = request.tracer.user.joined_project.all()
    created_projects = request.tracer.user.project_set.all()
    # 查询我创建的所有项目
    # 查询我参与的所有项目
    return locals()


@register.inclusion_tag('inclusion_tag/project_home_panel.html')
def project_panel(projects: QuerySet, panel_name: str, project_type: str = ""):
    return locals()


@register.inclusion_tag('inclusion_tag/manage_nav_bar.html')
def manage_nav_bar(request, project):
    """
    :param project:
    :return:
    """
    # ToDo 优化这里的渲染逻辑 不要耦合
    titles = ('Project:({})'.format(project.name), '问题', '统计', 'wiki', '文件', '配置')
    urls = ('dashboard', 'issues', 'statistics', 'wiki', 'file', 'settings')

    data = []
    for title, url in zip(titles, urls):
        tmp = dict()
        tmp['title'] = title
        tmp['url'] = reverse(url, kwargs={'project_id': project.id})
        if request.path_info.startswith(tmp['url']):
            tmp['class'] = 'active'
        data.append(tmp)

    content = {
        'data': data
    }
    return content
