from django.http import HttpResponse
from web.decorators import check_logging


@check_logging
def index(request):
    return HttpResponse('这是索引主页')
