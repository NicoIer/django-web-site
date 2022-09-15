from django.http import JsonResponse
from django_redis import get_redis_connection
from django.shortcuts import HttpResponse, HttpResponseRedirect, render

from web.forms.account import RegisterModelForm, EmailForm, LoginForm


def register(request):
    # return render(request)

    if request.method == 'GET':
        form = RegisterModelForm()
        return render(request, 'web/register.html', locals())
    elif request.method == 'POST':
        form = RegisterModelForm(data=request.POST)
        # return JsonResponse({'status': True, 'href': '/web/login/'})
        # 注释掉这些 测试跳转
        if form.is_valid():
            instance = form.save()
            return JsonResponse({'status': True, 'href': '/web/login/'})
        else:
            return JsonResponse({'status': False, 'error': form.errors})


def send_mail(request):
    # 这个路由存在的意义:当要求发送邮箱时做的操作
    if request.method == 'GET':
        email_form = EmailForm(data=request.GET)
        if email_form.is_valid():  # 验证通过则 发邮箱(同时存redis)
            return JsonResponse({'status': True})
        else:
            return JsonResponse({'status': False, 'error': email_form.errors})
    else:
        pass


def login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'web/login.html', locals())
    elif request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            return JsonResponse({'status': True, 'href': '/index/'})
        else:
            return JsonResponse({'status': False, 'error': form.errors})
