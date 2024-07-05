from django.db import models # type: ignore
from django.core.validators import RegexValidator # type: ignore
from django.contrib.postgres.fields import ArrayField # type: ignore
from django.contrib.auth.models import User # type: ignore


# Create your models here.
class CourseModel(models.Model):
    FLAG1 = 'Trending'
    FLAG2 = 'Upselling'
    FLAGS = [
        (FLAG1, "Trending"),
        (FLAG2, "Upselling")
    ]
    course_title = models.CharField(max_length=255)
    total_modules = models.CharField(max_length=10,validators=[RegexValidator(regex="^[1-9][0-9]*$",message="Please enter only numbers")])
    version = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=15,decimal_places=2)
    cover_image = models.ImageField(upload_to="course_cover_images/", max_length=255)
    course_author = models.CharField(max_length=255, null=True, blank=False)
    course_expertise = models.TextField(null=True, blank=False)
    flag = ArrayField(models.CharField(max_length=100, choices=FLAGS),null=True, blank=True)
    status = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ModuleModel(models.Model):
    OPTION1 = 'Audio'
    OPTION2 = 'Video'
    OPTION3 = 'Document'

    MODULE_TYPES = [
        (OPTION1, "Audio"),
        (OPTION2, "Video"),
        (OPTION3, "Document")
    ]

    course = models.ForeignKey(CourseModel, on_delete=models.PROTECT)
    module_title = models.CharField(max_length=255)
    material_title = models.CharField(max_length=255, null=True, blank=False)
    order = models.CharField(max_length=255, validators=[RegexValidator(regex="^[1-9][0-9]*$",message="Please enter only numbers")])
    
    duration_days = models.CharField(max_length=10)
    duration_months = models.CharField(max_length=10)
    module_type = ArrayField(models.CharField(max_length=100, choices=MODULE_TYPES),default=None)
    status = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ModulesMediaFile(models.Model):
    module = models.ForeignKey(ModuleModel, on_delete=models.CASCADE)
    uploaded_file = models.FileField(upload_to="modules_media/", null=True, blank=True)
    link= models.TextField(null=True, blank=True)
    file_type = models.CharField(max_length=50, null=True, blank=True)
    file_extension = models.CharField(max_length=50, null=True, blank=True)
    order = models.CharField(max_length=50, null=True, blank=True, validators=[RegexValidator(regex="^[0-9]*(\.[0-9]{1,2})?$",message="Please enter only numbers or decimals")])
    created_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    module = models.ForeignKey(ModuleModel, on_delete=models.CASCADE)
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.TextField()
    is_correct_answer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PopupQuestion(models.Model):
    popup_show_time = models.CharField(max_length=255, null=True, blank=True)
    module = models.ForeignKey(ModuleModel, on_delete=models.CASCADE)
    popup_question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PopupChoice(models.Model):
    popup_question = models.ForeignKey(PopupQuestion, on_delete=models.CASCADE)
    popup_choice_text = models.TextField()
    is_correct_answer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Subscription(models.Model):
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE)
    user = models.ManyToManyField(User)
    price = models.DecimalField(max_digits=15,decimal_places=2)
    discount = models.DecimalField(max_digits=15,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)