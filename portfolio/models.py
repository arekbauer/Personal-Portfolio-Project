from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    image = models.ImageField(upload_to='portfolio/images/')
    url = models.URLField(blank=True)
    skill1 = models.CharField(max_length=16, null=True, blank=True)
    skill2 = models.CharField(max_length=16, null=True, blank=True)
    skill3 = models.CharField(max_length=16, null=True, blank=True)
    skill4 = models.CharField(max_length=16, null=True, blank=True)
    
class Intro(models.Model):
    description = models.TextField()
    image = models.ImageField(upload_to='portfolio/images/', null=True)
    
class Timeline(models.Model):
    title = models.CharField(max_length=30)
    subtitle = models.CharField(max_length = 30, null=True)
    start_date = models.PositiveSmallIntegerField()
    end_date = models.PositiveSmallIntegerField(blank=True, null=True)
    description = models.TextField()
    
    @property
    def end_date_is_null(self):
        return self.end_date or "Present"