from django.http import HttpResponse
from django.shortcuts import render, redirect

from web import models
from web.utils import check_login


@check_login
def issues_home(request, project_id):
    try:
        project = models.Project.objects.get(id=project_id)
    except Exception:
        return redirect('project_list')

    return render(request, 'web/issue_home.html', locals())
