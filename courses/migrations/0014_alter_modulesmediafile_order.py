# Generated by Django 4.2.5 on 2023-10-26 04:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0013_popupquestion_popupchoice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modulesmediafile',
            name='order',
            field=models.CharField(blank=True, max_length=50, null=True, validators=[django.core.validators.RegexValidator(message='Please enter only numbers or decimals', regex='^[0-9]*(\\.[0-9]{1,2})?$')]),
        ),
    ]
