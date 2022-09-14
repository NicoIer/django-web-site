from django_redis import get_redis_connection
from django.shortcuts import HttpResponse, HttpResponseRedirect, render

from web.forms.account import RegisterModelForm


def register(request):
    # return render(request)
    form = RegisterModelForm()
    return render(request, 'web/register.html', locals())
