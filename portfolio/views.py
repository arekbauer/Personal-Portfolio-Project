from django.shortcuts import render
from collections import Counter
from .models import Project
from .models import Intro
from .models import Timeline

def home(request):
    projects = Project.objects.all()
    intros = Intro.objects.all()
    timelines = Timeline.objects.all()
    return render(request, 'portfolio/home.html', {'projects': projects, 'intros': intros, 'timelines': timelines})

def most_common_skills_view(request):
    print("Going into function")
    projects = Project.objects.all()
    all_skills = []
    
    for project in projects:
        skills = [project.skill1, project.skill2, project.skill3, project.skill4]
        # Filter out None or empty values
        all_skills.extend([skill for skill in skills if skill])
    
    skill_counts = Counter(all_skills)
    most_common_skills = [skill for skill, _ in skill_counts.most_common(4)]
    print(most_common_skills)
    
    return render(request, 'portfolio/projects.html', {
        'projects': projects,
        'most_common_skills': most_common_skills
    })