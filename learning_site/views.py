from django.shortcuts import render

from web.models import User


def index(request):
    uid = request.session.get('uid', None)
    if uid:
        user = User.objects.get(id=uid)
        return render(request, 'index.html', {'user':user})
    else:
        return render(request, 'index.html')
