from django.urls import path
from .views import initiate_payment, callback
from django.urls import path, register_converter

from . import converters

register_converter(converters.FloatUrlParameterConverter, 'float')

app_name = 'payment_app'

urlpatterns = [
    path('pay/<int:user_id>/<int:course_id>/', initiate_payment, name='pay'),
    path('callback/', callback, name='callback'),
]



