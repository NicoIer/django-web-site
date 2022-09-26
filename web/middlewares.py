from django.utils.deprecation import MiddlewareMixin

from web.utils import Tracer


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 每次都为request添加一个tracer属性 用于追踪部分信息
        request.tracer = Tracer()
