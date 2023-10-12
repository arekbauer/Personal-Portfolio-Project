from django.shortcuts import render
from .models import Project
from .models import Intro

def home(request):
    projects = Project.objects.all()
    intros = Intro.objects.all()
    return render(request, 'portfolio/home.html', {'projects': projects, 'intros': intros})
