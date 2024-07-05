from django import template
from django.utils.html import format_html
from django.contrib.admin.templatetags import admin_list
from django.utils.safestring import mark_safe
from django.contrib.admin.views.main import (
    ALL_VAR,
    IS_POPUP_VAR,
    ORDER_VAR,
    PAGE_VAR,
    SEARCH_VAR,
)

register = template.Library()

@register.inclusion_tag('admin/pagination.html',takes_context=True)
def custom_pagination(context, cl, custom_data=None):
    pagination = admin_list.pagination(cl)
    pagination['custom_data'] = custom_data
    return pagination

@register.simple_tag
def custom_paginator_number(cl, i):
    """
    Generate an individual page index link in a paginated list.
    """
    if i == cl.paginator.ELLIPSIS:
        return format_html('<li class="page-item"><a class="page-link">{}</a></li>', cl.paginator.ELLIPSIS)
    elif i == cl.page_num:
        return format_html('<li class="page-item active" aria-current="page"><a class="page-link">{}</a></li> ', i)
    else:
        return format_html(
            '<li class="page-item"><a href="{}"{}>{}</a></li>',
            cl.get_query_string({PAGE_VAR: i}),
            mark_safe(' class="page-link end"' if i == cl.paginator.num_pages else 'class="page-link"'),
            i,
        )
    
@register.simple_tag
def start_index(cl, page, counter):
    if cl is not None and cl.paginator is not None:
        pageobj = cl.paginator.page(page)
        return pageobj.start_index() + counter
    return None

@register.filter
def has_previous(cl):
    if cl is not None and cl.paginator is not None:
        pageobj = cl.paginator.page(cl.page_num)
        return pageobj.has_previous()
    return None

@register.filter
def has_next(cl):
    if cl is not None and cl.paginator is not None:
        pageobj = cl.paginator.page(cl.page_num)
        return pageobj.has_next()
    return None

@register.simple_tag
def next_page_num(cl):
    if cl is not None and cl.paginator is not None:
        pageobj = cl.paginator.page(cl.page_num)
        return cl.get_query_string({PAGE_VAR: pageobj.next_page_number()}) if pageobj.has_next() else pageobj.end_index
    return None

@register.simple_tag
def previous_page_num(cl):
    if cl is not None and cl.paginator is not None:
        pageobj = cl.paginator.page(cl.page_num)
        return cl.get_query_string({PAGE_VAR: pageobj.previous_page_number()}) if pageobj.has_previous() else 1
    return None