import hashlib
from web.models import User
from django.conf import settings
from django.http import HttpResponse
import uuid


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


def md5(string) -> str:
    hash_obj = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
    hash_obj.update(string.encode('utf-8'))
    return hash_obj.hexdigest()


def uid(string: str):
    return md5("{}-{}".format(uuid.uuid4(), string))
