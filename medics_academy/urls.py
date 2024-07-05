from django.contrib import admin 
from django.urls import path,include 
from django.conf.urls.static import static
from django.conf import settings 
from courses.admin import medics_admin_site


from users.urls import urlpatterns as usersurl 
from django.conf.urls import include

from courses.views import MediaFileView
from users.views import ModuleMediaFileView,UserProfileViews

handler404 = 'courses.views.error_404_view'
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('admin/', medics_admin_site.urls),
    path('', include("users.urls", namespace="user_app")), 
    # path('media/course_cover_images/<str:file_path>/', MediaFileView.course_media_view, name='course_media_view'), # type: ignore
    # path('<str:course_id>/media/modules_media/<str:file_path>/', ModuleMediaFileView.module_media_view, name='module_media_view'),
    #path('media/user_profile_images/<str:file_path>/', UserProfileViews.user_profile_media_view, name='user_profile_media_view'),
    #path('<str:course_id>/<str:media_id>/<str:signed_value>/', ModuleMediaFileView.module_media_signed_view, name='module_media_signed_view'),
    # path('payment/', include("payment.urls", namespace="payment_app")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
