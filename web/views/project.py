from django.shortcuts import render


def home(request):
    return render(request, r'web\project_home.html')
