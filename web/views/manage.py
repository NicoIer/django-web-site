from django.shortcuts import render


def dashboard(request, project_id: int, *args, **kwargs):
    return render(request, 'web/dashboard.html', locals())
