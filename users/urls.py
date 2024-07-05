from django.urls import path, reverse_lazy
from django.conf import settings
from django.conf.urls import handler404 



from . import views 
from django.contrib.auth import views as auth # type: ignore
from django.contrib.auth import views as auth_views
from users.views import HomePageViews
app_name = 'user_app'

urlpatterns = [

     path("", views.HomePageViews.landing_page, name="landing_page"),
    

     path("login/", views.UserAuthendication.user_login, name="user_login"),
     path('activate/<uidb64>/<token>', views.UserAuthendication.activate, name='activate'),
   
     path("register/", views.UserAuthendication.register, name="userRegistration"),
     path("dashboard/",views.UserAuthendication.user_dash, name="user_dash"),
     path("dashboard_first/",views.UserAuthendication.user_dash_first, name="user_dash_first"),
     path("user_logout/",views.UserAuthendication.user_logout,name="user_logout"),
     path("user_profile_list/",views.UserProfileViews.user_general_view,name="user_profile_list"),
     path("user_courses/",views.Purchased.purchased_course,name="user_courses"),
     path("user_profile_edit/",views.UserProfileViews.user_edit_profile,name="user_profile_edit"),
      path("user_password_change_profile", views.UserProfileViews.user_password_change_profile,name="user_password_change_profile"),
     path("view_course/<int:pk>/", views.HomePageViews.course_detail, name="courseview"),
     # path("subscription_view/<int:pk>/",views.HomePageViews.offer_detail, name="subview"),
     # path("user_learn/<int:course_pk>/", views.HomePageViews.user_learn, name="userlearn"),
     path("module_assesment/<int:pk>/", views.HomePageViews.user_assesment,name="moduleasses"),
     path("payment/<int:pk>/", views.HomePageViews.course_payment, name="coursepayment"),
     path('add_to_saved/<int:user_id>/<int:course_id>/', views.SavedPage.add_to_saved, name='add_to_saved'),
     path('remove_from_saved/<int:user_id>/<int:course_id>/', views.SavedPage.remove_from_saved, name='remove_from_saved'),

     path('saved_page/', views.SavedPage.save_page, name='saved_page'),
     path('saved_check/<int:user_id>/<int:course_id>/', views.SavedPage.saved_check, name='saved_check'),
     path('search_course/',views.Search.search_courses,name='search'),
     path('about_us/',views.HomePageViews.about_us,name='about_us'),
     # path('contact_us/',views.HomePageViews.contact_us,name='contact_us'),
     path('contact_us_message/',views.HomePageViews.contact_us_message,name='contact_us_message'),
     path('reset_password/',auth_views.PasswordResetView.as_view(template_name="registration/reset_password.html",success_url=reverse_lazy('user_app:password_reset_done'), html_email_template_name='registration/password_reset_email.html'),name='password_reset'),
     path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
     path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(success_url = reverse_lazy('user_app:password_reset_complete')), name='password_reset_confirm'),

     path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='login.html'), name='password_reset_complete'),
     path('add_to_purchased/<int:user_id>/<int:course_id>/', views.Purchased.add_to_purchase, name='add_to_purchase'),
     path("user_learn/<int:course_pk>/", views.Purchased.learning, name="learning"),
     path("assessment_submit/", views.assessment_submit, name="assessment_submit"),

     # path("average_submit/<int:user_id>/<int:module_id>/",views.view_average_mark,name="assesment_mark"),

     # path("user_mt_token/", views.Purchased.set_material_token, name="material_token")
     path("get_popup_question/", views.Purchased.get_popup_question, name="get_popup_question"),
     path("store_course_progress/", views.Purchased.store_course_progress, name="store_course_progress"),


]


     # path("error/", views.error_page.error_404, name="error")
     




