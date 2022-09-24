from django.shortcuts import render

from web.decorators import check_login
from web.forms.project import ProjectModelForm
from web.models import User, Project
from django.http import JsonResponse


@check_login
def project_home(request):
    """
    :param request:
    :return:
    """
    if request.method == 'GET':
        # check logging后 tracer必定是User
        user = request.tracer.user
        form = ProjectModelForm()
        contents = {'user': user, 'form': form}
        return render(request, r'web\project_home.html', contents)
    elif request.method == 'POST':
        form = ProjectModelForm(tracer=request.tracer, data=request.POST)
        if form.is_valid():
            # 验证通过
            form.instance.creator = request.tracer.user
            # 保存数据到数据库
            form.save()
            #
            return_data = {
                'status': True,
                'error': form.errors
            }
            return JsonResponse(return_data)
        else:
            return_data = {
                'status': False,
                'error': form.errors
            }
            return JsonResponse(data=return_data)
