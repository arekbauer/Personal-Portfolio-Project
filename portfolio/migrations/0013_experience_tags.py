# Generated by Django 5.0.7 on 2025-05-24 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0012_intro_image_small'),
    ]

    operations = [
        migrations.AddField(
            model_name='experience',
            name='tags',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
