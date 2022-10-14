from django.http import HttpResponse
from django.shortcuts import render, redirect

from web import models
from web.utils import check_login
from web.forms.issues import IssuesModelForm


@check_login
def issues_home(request, project_id):
    try:
        project = models.Project.objects.get(id=project_id)
    except Exception:
        return redirect('project_list')
    if request.method == 'GET':
        form = IssuesModelForm(project=project, method='GET')
        return render(request, 'web/issue_home.html', locals())
