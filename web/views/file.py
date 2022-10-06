from django.forms import model_to_dict
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
        # 获取当前文件夹所在路径
        dir_path = get_dir_path(parent_obj)
        # 获取所在文件夹下的所有文件 先文件夹 再文件
        file_list = models.FileRepository.objects.filter(project=project, parent=parent_obj).order_by('-file_type')

        form = FileFoldModelForm()
        return render(request, 'web/file_home.html', locals())
    elif request.method == 'POST':
        try:
            fid: str = request.POST.get('fid', "")
            edit_obj = models.FileRepository.objects.get(id=int(fid), file_type=2, project=project)
        except Exception:
            edit_obj = None

        form = FileFoldModelForm(parent_id=parent_id, project=project, data=request.POST, instance=edit_obj)
        if form.is_valid():
            form.instance.project = project
            form.instance.file_type = 2
            form.instance.update_user = request.tracer.user
            form.instance.parent = parent_obj
            form.save()
            return JsonResponse({'status': True, 'error': form.errors})
        else:
            return JsonResponse({'status': False, 'error': form.errors})


def get_dir_path(cur_folder):
    breadcrumb_list = []
    _ = cur_folder
    while _:
        breadcrumb_list.append(_)
        _ = _.parent

    breadcrumb_list.reverse()
    return breadcrumb_list


@check_login
def file_delete(request, project_id):
    fid = request.GET.get('fid', "")
    try:
        # 删除了数据库中的文件夹/文件
        # 若是文件 则需要 在minIO中删除
        file = models.FileRepository.objects.get(id=fid, project_id=project_id)
        if file.file_type == 1:
            pass
        elif file.file_type == 2:
            pass
        else:
            raise "????"
        file.delete()
    except Exception:
        return JsonResponse({'status': False})
    return JsonResponse({'status': True})
