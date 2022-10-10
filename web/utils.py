import asyncio
import datetime
import hashlib
import json
import uuid
from datetime import timedelta

import minio.error
from django.conf import settings
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.http import HttpResponse
from django.shortcuts import redirect
from minio import Minio
from minio.deleteobjects import DeleteObject
from minio.error import InvalidResponseError

from web import models
from web.forms.project import ProjectModelForm
from web.models import User


class Tracer(object):
    def __init__(self):
        self.user = None
        self.price_policy = None


def check_login(func):
    # ToDo 太多的地方用到了 check_login 而 部分的查询是重复多余的 想要优化
    def warp(request: HttpRequest, *args, **kwargs):
        if request.session.get('uid', None) or request.COOKIES.get('uid', None):
            uid = request.COOKIES.get('uid')
            request.session['uid'] = uid
            request.session['username'] = request.COOKIES.get('username')
            try:
                # 查询这个user 并存储
                request.tracer.user = User.objects.get(id=uid)
            except Exception:
                return HttpResponseRedirect('/web/login/')

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


class MinIoManager:
    def __init__(self, user=settings.MINIO_ACCESS_KEY,
                 password=settings.MINIO_SECRET_KEY,
                 host=settings.MINIO_HOST,
                 port=settings.MINIO_PORT,
                 region=settings.MINIO_DEFAULT_REGION,
                 secure=False
                 ):

        self.client = Minio('{}:{}'.format(host, port),
                            access_key=user,
                            secret_key=password,
                            secure=secure,
                            region=region,
                            )

    def create_bucket(self, bucket_name: str, location: str = None, policy: dict = None) -> bool:
        try:
            self.client.make_bucket(bucket_name, location)
        except minio.error.S3Error:
            return False
        if policy:
            pass
        return True

    def set_bucket_public_read(self, bucket_name):
        # ToDo 有点丑  想办法修改一下
        policy_json = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicRead",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": [
                        "s3:GetObject",
                        "s3:GetObjectVersion"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{bucket_name}/*"
                    ]
                }
            ]
        }
        self.client.set_bucket_policy(bucket_name, json.dumps(policy_json))

    def upload_iostream(self, bucket_name, obj_name, data, length) -> bool:
        try:
            self.client.put_object(bucket_name, obj_name, data, length)
        except Exception:
            raise

        return True

    def delete_obj(self, bucket_name, obj_name):
        try:
            self.client.remove_object(bucket_name, obj_name)
        except InvalidResponseError:
            raise

    async def async_delete_obj(self, bucket_name, obj_name):
        # ToDo 实现异步删除
        raise NotImplementedError

    def delete_objs(self, bucket_name, obj_name_list):
        try:
            obj_name_list = list(map(lambda x: DeleteObject(x), obj_name_list))
            errors = self.client.remove_objects(bucket_name, obj_name_list)
            for error in errors:
                print("Deletion Error: {}".format(error))
        except InvalidResponseError:
            raise

    async def delete_bucket_async(self, bucket_name):
        return self.delete_bucket(bucket_name)

    def delete_bucket(self, bucket_name):
        try:
            object_names = list(map(lambda x: x.object_name, self.client.list_objects(bucket_name, recursive=True)))
            self.delete_objs(bucket_name, object_names)
            self.client.remove_bucket(bucket_name)
        except minio.S3Error as e:
            print(e)

    def get_obj_put_url(self, bucket_name, obj_name, delta=timedelta(days=2)) -> str:
        try:
            url = self.client.presigned_put_object(bucket_name, obj_name, delta)
        except Exception:
            raise
        return url

    def get_obj_get_url(self, bucket_name, obj_name, delta=timedelta(days=2)) -> str:
        try:
            url = self.client.presigned_get_object(bucket_name, obj_name, delta)
        except Exception:
            raise
        return url


minio_manager = MinIoManager()


def check_form(form: ProjectModelForm, request: HttpRequest) -> JsonResponse:
    if form.is_valid():
        # ToDo 这里可能会有异常 为项目创建一个Bucket
        _ = models.Project.objects.last()
        _id = _.id + 1 if _ else 1
        # toDo 这里可能会有并发异常...
        bucket_name = '{}-{}'.format(request.tracer.user.id, (_id + 1))
        location = settings.MINIO_DEFAULT_REGION

        minio_manager.create_bucket(bucket_name, location)
        # 为项目属性赋值
        form.instance.bucket = bucket_name
        form.instance.region = location

        # 验证通过
        form.instance.creator = request.tracer.user
        # 保存数据到数据库
        form.save()
        #
        return_data = {
            'status': True,
            'error': form.errors
        }
        return JsonResponse(return_data)
    else:
        return_data = {
            'status': False,
            'error': form.errors
        }
        return JsonResponse(data=return_data)


def update_project_star(request: HttpRequest, project_type: str, project_id: int) -> HttpResponse:
    try:
        project = models.Project.objects.get(id=project_id, creator=request.tracer.user)
    except Exception:
        return HttpResponse("???")
    remove = project.star
    project.star = not project.star
    project.save()

    if project_type == 'my' or project_type == 'star' or (
            project_type == 'join' and project in request.tracer.user.joined_project.all()):  #
        if remove:
            request.tracer.user.stared_project.remove(project_id)
        else:
            request.tracer.user.stared_project.add(project_id)

        return redirect('project_list')
    else:
        return HttpResponse("?????")


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
