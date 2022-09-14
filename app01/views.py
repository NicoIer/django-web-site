from django.shortcuts import render

from .models import *


# Create your views here.
def index(request):
    return None


def register(request):
    form = RegisterModelForm()
    return render(request, 'app01/register.html', locals())
