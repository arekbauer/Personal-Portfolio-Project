# Generated by Django 5.0 on 2023-12-19 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0009_project_skill1_project_skill2_project_skill3_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='skill1',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='skill2',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='skill3',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='skill4',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
