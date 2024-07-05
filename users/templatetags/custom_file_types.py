from django import template

register = template.Library()

@register.filter
def count_file_type(modulesmf, file_type):
   
    return modulesmf.filter(file_type=file_type).count()
