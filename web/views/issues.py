from django.http import HttpResponse, JsonResponse
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


@check_login
def issue_from_check(request, project_id):
    try:
        project = models.Project.objects.get(id=project_id)
    except Exception:
        return redirect('project_list')
    if request.method == 'POST':
        form = IssuesModelForm(project=project, method='POST', data=request.POST)
        if form.is_valid():
            form.instance.project = project
            form.instance.creator = request.tracer.user
            form.save()
            return JsonResponse({'status': True})
        else:
            return JsonResponse({'status': False, 'error': form.errors})
