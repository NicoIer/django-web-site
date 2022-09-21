from django.http import HttpResponse, HttpRequest, HttpResponseRedirect

from web.models import User


def check_login(func):
    def warp(request: HttpRequest, *args, **kwargs):
        if request.session.get('uid', None) or request.COOKIES.get('uid', None):
            uid = request.COOKIES.get('uid')
            request.session['uid'] = uid
            request.session['username'] = request.COOKIES.get('username')
            # 查询这个user 并存储
            request.tracer = User.objects.get(id=uid)
            if request.tracer is None:
                return HttpResponseRedirect('/web/login/')
            else:
                return func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/web/login/')

    return warp
