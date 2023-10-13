from django.contrib import admin
from .models import Project
from .models import Intro
from .models import Timeline

admin.site.register(Project)
admin.site.register(Intro)
admin.site.register(Timeline)