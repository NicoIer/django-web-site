from django.shortcuts import render

from web.decorators import check_login
from web.forms.project import ProjectModelForm
from web.models import User


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
        pass
