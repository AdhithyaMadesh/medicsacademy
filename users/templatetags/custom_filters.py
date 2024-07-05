from django import template
from courses .models import CourseModel
from users .models import  CourseProgress
from django.db.models import Count ,Sum

register = template.Library()

@register.filter
def remove_spaces(value):
    return value.replace(" ", "")


@register.filter
def modulus(value, arg):
    return value % arg

@register.filter
def convert_to_signed_val(value):
    from django.core.signing import Signer
    signer = Signer()
    signval = signer.sign(value.id)
    return signval.split(':')[1]



@register.filter
def purchased_course_progress_percentage(user,course):
    percentage = 0
    latest_course_detail = CourseProgress.objects.filter(course=course,user=user)
    
    if latest_course_detail:
        latest_course_detail = latest_course_detail.latest("watched_date")
        # print(latest_course_detail)
        related_modules = user.purchasedcourse_set.filter(courses=latest_course_detail.course).first().courses.modulemodel_set
        # print(f"realted_moules : {related_modules}")
        completed_aseessment_count = 0
        for i in related_modules.all():
            # count=i.attemptedassessment_set.filter(user=user).count()
            # print(f" count:{count}")
            # print(f" i:{i}")
            completed_aseessment_count += 1 if i.attemptedassessment_set.filter(user=user).count() > 0 else 0
        # print(f"completed_aseessment_count:{completed_aseessment_count}")    

        progress_count = CourseProgress.objects.filter(user=user,course=latest_course_detail.course).count()+completed_aseessment_count
        # print(progress_count)
        total_media_count = latest_course_detail.course.modulemodel_set.filter(status=True).annotate(mmf_count=Count('modulesmediafile')).aggregate(Sum("mmf_count", default=0))
        total_media_count = total_media_count['mmf_count__sum']+related_modules.count()
        # print(total_media_count)
        percentage = round((progress_count/total_media_count)*100)

    return percentage

