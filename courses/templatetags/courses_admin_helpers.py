from django import template
from datetime import datetime
from courses.models import CourseModel
from users.models import CourseProgress
from django.db.models import Count, Sum

register = template.Library()

@register.filter
def crange(min, max):
    return range(min, max)

@register.filter
def to_int(value):
    return int(value)

@register.filter
def split_n_check(value, splitstr, delimiter=','):
    if value in splitstr.split(delimiter):
        return True
    else:
        return False
    
@register.filter
def split_n_join(value):
    return ', '.join(value)

@register.filter
def split_n_checklist(value, splitlist):
    if value in splitlist:
        return True
    else:
        return False
    
@register.filter
def join_list(value):
    return ','.join(value)

@register.filter
def get_list(dictionary, name):
    return dictionary.getlist(name)

@register.filter
def get_values_list(qset, name, flatopt = True):
    return list(qset.values_list(name, flat=flatopt))

@register.filter
def base64(read_img,name):
    if read_img:
        import base64
        return base64.b64encode(read_img.get(name).read()).decode('utf-8')
    else:
        return ''

@register.filter
def file_content_type(rfile, name):
    if rfile:
        return rfile.get(name).content_type
    else:
        return ''
    
@register.filter
def days_until(date):
    delta = datetime.now().date() - datetime.date(date)
    return delta.days

@register.filter
def purchased_courses_duration(user):
    course_ids = [pcourse.courses_id for pcourse in user.purchasedcourse_set.all()]
    months = 0
    days = 0
    for i in course_ids:
        modules = CourseModel.objects.get(pk=i).modulemodel_set.all()
        for j in modules:
            months += int(j.duration_months)
            days += int(j.duration_days)
    return str(months)+ ' months '+ str(days) + ' days'

@register.filter
def last_purchased_course_progress(user):
    percentage = 0
    latest_course_detail = CourseProgress.objects.filter(user=user)
    if latest_course_detail:
        latest_course_detail = latest_course_detail.latest("watched_date")
        related_modules = user.purchasedcourse_set.filter(courses=latest_course_detail.course).first().courses.modulemodel_set
        completed_aseessment_count = 0
        for i in related_modules.all():
            completed_aseessment_count += 1 if i.attemptedassessment_set.filter(user=user).count() > 0 else 0

        progress_count = CourseProgress.objects.filter(user=user,course=latest_course_detail.course).count()+completed_aseessment_count
        total_media_count = latest_course_detail.course.modulemodel_set.filter(status=True).annotate(mmf_count=Count('modulesmediafile')).aggregate(Sum("mmf_count", default=0))
        total_media_count = total_media_count['mmf_count__sum']+related_modules.count()
        percentage = round((progress_count/total_media_count)*100)

    return percentage