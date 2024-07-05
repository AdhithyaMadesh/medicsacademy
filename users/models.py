from django.db import models




from django.contrib.auth.models import User
from courses .models import CourseModel ,ModuleModel,Question,Choice, ModulesMediaFile

from payment .models import Payment

# Create your models here.
class UserProfileModel(models.Model):
    GENDER_CHOICES = [
        ('F', 'Female'),
        ('M', 'Male'),
        ('O', 'Others'),
    ]

    OCCUPATION = [
        ("S", "Student"),
        ("T", "Teacher"),
        ("O", "Others")
    ]



    user = models.ForeignKey(User, on_delete=models.CASCADE)
    country_code = models.CharField(max_length=10, default=None)
    phone_number = models.CharField(max_length=10)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    occupation = models.CharField(max_length=1, choices=OCCUPATION)
    occupation_others = models.CharField(max_length=255, blank=True)
    college = models.CharField(max_length=255, blank=True)
    profile_img = models.ImageField(upload_to='user_profile_images/', null=True)





class SavedCourses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE)


class PurchasedCourse(models.Model):
    users = models.ForeignKey(User, on_delete=models.CASCADE)
    courses = models.ForeignKey(CourseModel , on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)







class AttemptedAssessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(ModuleModel,on_delete=models.CASCADE)
    question = models.ForeignKey(Question,on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice,on_delete=models.CASCADE)
    assessment_date = models.DateField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)

class CourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseModel , on_delete=models.CASCADE)
    module = models.ForeignKey(ModuleModel,on_delete=models.CASCADE)
    modulemediafile = models.ForeignKey(ModulesMediaFile, on_delete=models.CASCADE)
    watched_date = models.DateTimeField(auto_now_add=True)






class ReAssessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(ModuleModel,on_delete=models.CASCADE)
    question = models.ForeignKey(Question,on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice,on_delete=models.CASCADE)
    assessment_date = models.DateField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)



class ReAssessmentAverage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseModel , on_delete=models.CASCADE)
    module = models.ForeignKey(ModuleModel,on_delete=models.CASCADE)
    reassessment_date = models.DateField(auto_now_add=True)
    average = models.DecimalField(max_digits=10, decimal_places=2)




