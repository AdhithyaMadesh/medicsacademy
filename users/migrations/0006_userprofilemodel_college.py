# Generated by Django 4.2.5 on 2023-10-09 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_userprofilemodel_occupation_others'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofilemodel',
            name='college',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]