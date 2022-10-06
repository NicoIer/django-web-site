from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render

from web import models
from web.forms.file import FileFoldModelForm
from web.utils import check_login


@check_login
def file_home(request, project_id):
    """file list"""
    try:
        project = models.Project.objects.get(id=project_id)
    except Exception:
        return render(request, 'index.html')
    # 获取当前所在文件夹id
    parent_id = request.GET.get('folder_id', "")
    parent_id = int(parent_id) if parent_id.isdigit() else None
    # 获取当前所在文件夹
    try:
        parent_obj = models.FileRepository.objects.get(id=parent_id, file_type=2, project=project)
    except Exception:
        parent_obj = None

    if request.method == 'GET':
        # 获取所在文件夹下的所有文件 先文件夹 再文件
        file_list = models.FileRepository.objects.filter(project=project, parent=parent_obj).order_by('-file_type')

        form = FileFoldModelForm()
        return render(request, 'web/file_home.html', locals())
    elif request.method == 'POST':
        # ToDo 这里非常丑！！！
        form = FileFoldModelForm(parent_id=parent_id, project=project, data=request.POST)
        # 再向这个文件夹下添加内容
        if form.is_valid():
            form.instance.project = project
            form.instance.file_type = 2
            form.instance.update_user = request.tracer.user
            form.instance.parent = parent_obj
            form.save()
            return JsonResponse({'status': True, 'error': form.errors})
        else:
            return JsonResponse({'status': False, 'error': form.errors})


def add_folder(request):
    pass
