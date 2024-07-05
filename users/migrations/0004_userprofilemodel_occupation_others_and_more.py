# Generated by Django 4.2.5 on 2023-10-06 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_userprofilemodel_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofilemodel',
            name='occupation_others',
            field=models.CharField(default=None, max_length=255),
        ),
        migrations.AlterField(
            model_name='userprofilemodel',
            name='occupation',
            field=models.CharField(choices=[('S', 'Student'), ('T', 'Teacher'), ('O', 'Others')], max_length=1),
        ),
    ]
