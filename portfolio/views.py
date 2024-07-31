from django.shortcuts import render
from collections import Counter
from .models import Project
from .models import Intro
from .models import Timeline

# def home(request):
#     projects = Project.objects.all()
#     intros = Intro.objects.all()
#     timelines = Timeline.objects.all()
#     return render(request, 'portfolio/home.html', {'projects': projects, 'intros': intros, 'timelines': timelines})

def home(request):
    projects = Project.objects.all()
    intros = Intro.objects.all()
    timelines = Timeline.objects.all()
    
    all_skills = []
    
    for project in projects:
        skills = [project.skill1, project.skill2, project.skill3, project.skill4]
        filtered_skills = [skill for skill in skills if skill] #filtering out None or empty values
        # Add the filtered skills to the all_skills list
        all_skills.extend(filtered_skills)
    
    # Use Counter to count occurrences of each skill
    skill_counts = Counter(all_skills)
    
    # Get the 4 most common skills
    most_common_skills = [skill for skill, _ in skill_counts.most_common(4)]
    
    return render(request, 'portfolio/home.html', {
        'projects': projects,              
        'intros': intros,                  
        'timelines': timelines,            
        'most_common_skills': most_common_skills,  
    })