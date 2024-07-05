# Generated by Django 4.2.5 on 2023-10-12 11:56

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_coursemodel_course_author_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursemodel',
            name='flag',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('Trending', 'Trending')], max_length=100), blank=True, null=True, size=None),
        ),
    ]
