from django.http import HttpResponse

from web.models import User


def login_cookie_session(request, response, user: User, max_age: int = 3600 * 24):
    # session会默认加密
    request.session['uid'] = user.id
    request.session['username'] = user.username
    response.set_cookie('uid', user.id, max_age=max_age)
    response.set_cookie('username', user.username, max_age=max_age)
    return response


def logout_cookie_session(request, response: HttpResponse):
    request.session.clear()
    request.COOKIES.clear()
    response.delete_cookie('username')
    response.delete_cookie('uid')
    return response
