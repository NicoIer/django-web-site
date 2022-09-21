from django.shortcuts import render

from web.decorators import check_login
from web.models import User


@check_login
def home(request):
    user = request.tracer
    return render(request, r'web\project_home.html', {'user': user})
