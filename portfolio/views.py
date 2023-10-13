from django.shortcuts import render
from .models import Project
from .models import Intro
from .models import Timeline

def home(request):
    projects = Project.objects.all()
    intros = Intro.objects.all()
    timelines = Timeline.objects.all()
    return render(request, 'portfolio/home.html', {'projects': projects, 'intros': intros, 'timelines': timelines})
