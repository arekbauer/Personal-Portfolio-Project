# Generated by Django 4.2.5 on 2023-12-19 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0007_alter_timeline_end_date_alter_timeline_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeline',
            name='end_date',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
