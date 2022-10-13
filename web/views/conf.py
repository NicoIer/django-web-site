import asyncio

from django.shortcuts import render

from web import models
from web.utils import check_login, minio_manager


@check_login
def home(request, project_id):
    try:
        project = models.Project.objects.get(id=project_id)
    except Exception:
        return render(request, 'index.html')
    return render(request, 'web/conf.html', locals())


@check_login
def delete(request, project_id):
    try:
        project = models.Project.objects.get(id=project_id)
    except Exception:
        return render(request, 'index.html')
    if request.method == 'GET':
        return render(request, 'web/delete_project.html', locals())


@check_login
def ensure_delete(request: object, project_id: object) -> object:
    try:
        project = models.Project.objects.get(id=project_id)
    except Exception:
        return render(request, 'index.html')
    if request.method == 'GET':
        # 只有项目创建者可以删除
        if project.creator == request.tracer.user:
            # 删除桶
            async def delete_async():
                # 删除文件
                delete_coroutine = minio_manager.delete_bucket_async(project.bucket)
                delete_task = asyncio.create_task(delete_coroutine)
                return await delete_task

            delete_result = asyncio.run(delete_async())
            # 删除MySQL记录
            # 删除与project有关联的user
            project.stared_user.clear()
            project.joined_user.clear()
            project.delete()
            return render(request, 'web/project_home.html', locals())
        else:
            error = '您不能删除其他用户创建的项目'
            return render(request, 'index.html', locals())
