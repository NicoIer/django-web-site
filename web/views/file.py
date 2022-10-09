import datetime
import queue
from collections import deque
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from minio.deleteobjects import DeleteObject

from web import models
from web.forms.file import FileFoldModelForm
from web.models import FileRepository
from web.utils import check_login, minio_manager
from web.views.util import uid, md5


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


@check_login
def file_delete(request, project_id):
    try:
        project = models.Project.objects.get(id=project_id)
    except Exception:
        return render(request, 'index.html')

    fid = request.GET.get('fid', "")
    try:
        # 删除了数据库中的文件夹/文件
        # 若是文件 则需要 在minIO中删除
        file = models.FileRepository.objects.get(id=fid, project_id=project_id)
        if file.file_type == 1:
            # 由于不设置最大存储容量....所以不用管 size的事情
            minio_manager.delete_obj(project.bucket, file.key)
        elif file.file_type == 2:  # 此时是Folder
            keys = get_all_files(file)
            minio_manager.delete_objs(project.bucket, keys)
        # 从数据库记录中删除
        file.delete()
    except Exception:
        return JsonResponse({'status': False})
    return JsonResponse({'status': True})


@check_login
def file_download(request):
    if request.method == 'GET':
        file_key = request.GET.get('file_key')
        bucket = request.GET.get('bucket')
        file_name = request.GET.get('file_name')
        _ = minio_manager.client.get_object(bucket, file_key)
        response = HttpResponse(_)
        response['Content-Disposition'] = f'attachment;filename="{file_name}"'
        return response


@check_login
def get_download_url(request):
    if request.method == 'GET':
        file_key = request.GET.get('file_key')
        bucket = request.GET.get('bucket')
        url = minio_manager.get_obj_get_url(bucket, file_key, delta=datetime.timedelta(minutes=5))
        return JsonResponse({'status': True, 'url': url})


@csrf_exempt
@check_login
def upload_success(request, project_id):
    try:
        project = models.Project.objects.get(id=project_id)
    except Exception:
        return render(request, 'index.html')
    # 文件上传成功的确认
    if request.method == 'POST':
        file_name = request.POST.get("file_name", "")
        file_size = request.POST.get("file_size", "")
        folder_id = request.POST.get('folder_id', "")
        if file_name:
            file_key = md5(file_name)
            _ = FileRepository(name=file_name, file_size=file_size,
                               file_type=1, project=project, key=file_key,
                               parent_id=folder_id,
                               update_user=request.tracer.user,
                               )
            _.save()
            return JsonResponse({'status': True})
        else:
            return JsonResponse({'status': False})


@csrf_exempt
@check_login
def get_upload_url(request):
    if request.method == 'POST':
        # POST 请求 返回 url
        bucket = request.POST.get('bucket')
        file_name = request.POST.get('file_name')
        folder_id = request.POST.get('folder_id')
        # 检查文件夹下是否有重名文件
        folder_id = folder_id if folder_id else None
        folder_files = get_cur_folder_files(folder_id)
        # 传入的bucket和文件名不为空 且 当前folder下不存在同名文件
        if bucket and file_name and not folder_files.filter(name=file_name).exists():
            # 检查这个文件名是否合法
            url = minio_manager.get_obj_put_url(request.POST.get('bucket'), md5(request.POST.get('file_name')))
            return JsonResponse({'status': True, 'url': url})
        else:
            return JsonResponse({'status': False})


def get_cur_folder_files(folder_id: FileRepository):
    return FileRepository.objects.filter(parent_id=folder_id, file_type=1)


def get_all_files(folder: FileRepository):
    folder_queue = deque()
    folder_queue.append(folder)
    files = []
    while folder_queue:
        folder = folder_queue.popleft()
        childes = folder.child.all()
        child_files = childes.filter(file_type=1)
        child_folders = childes.filter(file_type=2)
        for child_folder in child_folders:
            # print('{}的子文件夹{}'.format(folder.name, child_folder.name))
            folder_queue.append(child_folder)
        for file in child_files:
            files.append(file.key)
    return files


def get_dir_path(cur_folder):
    breadcrumb_list = []
    _ = cur_folder
    while _:
        breadcrumb_list.append(_)
        _ = _.parent

    breadcrumb_list.reverse()
    return breadcrumb_list
