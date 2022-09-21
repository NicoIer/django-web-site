from django.shortcuts import render

from web.decorators import check_login
from web.models import User


@check_login
def home(request):
    """
    :param request:
    :return:
    """
    # check logging后 tracer必定是User
    user = request.tracer.user
    return render(request, r'web\project_home.html', {'user': user})
