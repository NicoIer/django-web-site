from django.http import HttpResponse, HttpRequest, HttpResponseRedirect


def check_login(func):
    def warp(request: HttpRequest, *args, **kwargs):
        if request.session.get('uid', None) or request.COOKIES.get('uid', None):
            request.session['uid'] = request.COOKIES.get('uid')
            request.session['username'] = request.COOKIES.get('username')
            return func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/web/login/')

    return warp
