import datetime

from django.http import HttpResponse, HttpRequest, HttpResponseRedirect

from web import models
from web.models import User


class Tracer(object):
    def __init__(self):
        self.user = None
        self.price_policy = None


def check_login(func):
    def warp(request: HttpRequest, *args, **kwargs):
        if request.session.get('uid', None) or request.COOKIES.get('uid', None):
            uid = request.COOKIES.get('uid')
            request.session['uid'] = uid
            request.session['username'] = request.COOKIES.get('username')
            # 查询这个user 并存储
            request.tracer.user = User.objects.get(id=uid)

            if request.tracer.user is None:
                return HttpResponseRedirect('/web/login/')
            else:  # 这个用户存在,则允许通过装饰器
                # 顺便更新下用户的状态
                # ToDo 优化这个查询,耗时太长
                transaction = models.Transaction.objects. \
                    filter(user=request.tracer.user, status=2).order_by('-id').first()

                if transaction and transaction.end_datetime < datetime.datetime.now():
                    transaction = models.Transaction.objects. \
                        get(user=request.tracer.user, status=2, price_policy__category=1)
                    request.tracer.price_policy = transaction.price_policy

                return func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/web/login/')

    return warp
