from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from web import models
from web.forms.wiki import WikiModelForm
from web.utils import check_login


@check_login
def home(request, project_id: int):
    try:
        project = models.Project.objects.get(id=project_id)
    except Exception:
        return redirect('project_list')
    if (project in request.tracer.user.joined_project.all()) or (project in request.tracer.user.project_set.all()):
        wiki_id = request.GET.get('wiki_id', None)

        if wiki_id and wiki_id.isdecimal():
            wiki = models.Wiki.objects.get(id=wiki_id)

        return render(request, 'web/wiki.html', locals())
    else:
        return redirect('project_list')


@check_login
def delete(request, project_id, wiki_id):
    try:
        _ = models.Wiki.objects.get(project_id=project_id, id=wiki_id)
        _.delete()
    except Exception:
        return redirect('project_list')

    url = reverse('wiki', kwargs={'project_id': project_id})
    return redirect(url)


@check_login
def add(request, project_id: int):
    try:
        project = models.Project.objects.get(id=project_id)
    except Exception:
        return redirect('project_list')

    if request.method == 'GET':
        form = WikiModelForm(project=project, method='get')
        return render(request, 'web/wiki_form.html', locals())
    elif request.method == 'POST':
        form = WikiModelForm(method='post', project=project, data=request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': True, 'error': form.errors})
        else:
            return JsonResponse({'status': False, 'error': form.errors})


@check_login
def edit(request, project_id, wiki_id):
    try:
        wiki = models.Wiki.objects.get(id=wiki_id)
        project = models.Project.objects.get(id=project_id)
    except Exception:
        return render(request, 'index.html')
    # 使用 key 传参 避免GG
    if request.method == 'GET':
        form = WikiModelForm(instance=wiki, method='get', project=project)
    elif request.method == 'POST':
        form = WikiModelForm(instance=wiki, data=request.POST, method='post', project=project)
        if form.is_valid():
            wiki.save()
            # 不好看!
            url = reverse('wiki', kwargs={'project_id': project_id})
            url = '{}?wiki_id={}'.format(url, wiki_id)
            return JsonResponse({'status': True, 'errors': form.errors, 'href': url})

    return render(request, 'web/wiki_edit.html', locals())
