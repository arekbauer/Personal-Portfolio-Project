# Generated by Django 4.2.5 on 2023-10-17 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0005_timeline_subtitle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeline',
            name='subtitle',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='timeline',
            name='title',
            field=models.CharField(max_length=30),
        ),
    ]