# Generated by Django 4.2.5 on 2023-11-07 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_alter_reassessmentaverage_average'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofilemodel',
            name='profile_img',
            field=models.FileField(max_length=255, null=True, upload_to='user_profile_images/'),
        ),
    ]
