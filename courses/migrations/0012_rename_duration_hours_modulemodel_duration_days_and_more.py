# Generated by Django 4.2.5 on 2023-10-13 10:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0011_alter_coursemodel_flag'),
    ]

    operations = [
        migrations.RenameField(
            model_name='modulemodel',
            old_name='duration_hours',
            new_name='duration_days',
        ),
        migrations.RenameField(
            model_name='modulemodel',
            old_name='duration_minutes',
            new_name='duration_months',
        ),
        migrations.AddField(
            model_name='modulesmediafile',
            name='file_extension',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='modulesmediafile',
            name='file_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='modulesmediafile',
            name='order',
            field=models.CharField(blank=True, max_length=50, null=True, validators=[django.core.validators.RegexValidator(message='Please enter only numbers', regex='^[1-9][0-9]*$')]),
        ),
    ]