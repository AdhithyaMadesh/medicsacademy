from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import UserProfileModel
from django.conf import settings
from .forms import RegistrationForm, RegistrationForm1, UserProfileEdit, UserProfileChangePassword
from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
import sys
import random
from django.core.mail import send_mail, EmailMultiAlternatives,EmailMessage
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from .tokens import generate_token
from django.db.models import Count, Sum


from courses .models import CourseModel, ModuleModel, Question, ModulesMediaFile, PopupQuestion, Choice ,Subscription
from django.core.paginator import Paginator
from .models import SavedCourses, PurchasedCourse
from django.http import JsonResponse, Http404, FileResponse
from django.db.models import Q
from django.contrib.sessions.models import Session
from django.urls import reverse
import os
from django.views.decorators.csrf import requires_csrf_token
from django.utils import timezone
from .models import AttemptedAssessment, CourseProgress, ReAssessment, ReAssessmentAverage
from django.utils.html import strip_tags



# url = reverse('user_app:password_reset_done')
def check_purchased_course(view_func):
    def wrapper(request, pk, *args, **kwargs):
        module = get_object_or_404(ModuleModel, pk=pk)
        course_pk = module.course.id

        if not PurchasedCourse.objects.filter(users=request.user, courses__pk=course_pk).exists():
            return redirect('user_app:user_dash')
        return view_func(request, pk, *args, **kwargs)
    return wrapper

def module_calculation_decorator(func):
    def wrapper(request, course_id):
        course = get_object_or_404(CourseModel, pk=course_id)
        modules = course.modulemodel_set.all()
        total_module_days = 0
        total_module_months = 0

        for module in modules:
            duration_days = module.duration_days
            duration_months = module.duration_months
            total_module_days += int(duration_days)
            total_module_months += int(duration_months)

        total_days = total_module_days + (total_module_months * 30)
        course_months = total_days // 30
        course_days = total_days - course_months * 30

        # Call the original function with the calculated values
        return func(request, course_id, course_months, course_days)

    return wrapper

# Create your views here.


class UserAuthendication():

    def register(request):
        if request.user.is_authenticated:
            return redirect('user_app:user_dash')
        else:
            if request.method == 'POST':
                form = RegistrationForm(request.POST)
                step = request.POST['step']
                if step == '1':
                    if form.is_valid():
                        return JsonResponse({"success": True})
                    else:
                        errors = dict([(field, [error for error in errors])
                                      for field, errors in form.errors.items()])
                        return JsonResponse({"success": False, "errors": errors})

                form_1 = RegistrationForm1(request.POST)
                if step == '2' and form_1.is_valid():
                    email = request.POST['email']
                    name = request.POST['name']
                    gender = request.POST['gender']
                    country_code = request.POST['country_code']
                    phone_number = request.POST['phone_number']
                    password = request.POST['password']
                    occupation = request.POST['occupation']
                    college = request.POST['college']
                    occupation_others = request.POST['occupation_others']
                    reg = list(str(phone_number))
                    random_n = str(random.randint(1111, 99999))
                    uname = "reg"+random_n+"".join(reg[-4:])

                    user = User.objects.create_user(
                        username=uname,  email=email, password=password, is_superuser=False, is_staff=False, is_active=False)
                    user.first_name = name
                    user.save()

                    userprofile = UserProfileModel(
                        user=user,
                        gender=gender,
                        occupation=occupation,
                        occupation_others=occupation_others,
                        country_code=country_code,
                        phone_number=phone_number,
                        college=college
                    )
                    userprofile.save()

                    current_site = get_current_site(request)
                    email_subject = "Confirm Your Email Address"
                    html_body = render_to_string('email_confirmation.html', {
                        'name': uname,
                        'password': password,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': generate_token.make_token(user)
                    })
                    message = EmailMultiAlternatives(
                        subject=email_subject,
                        body="mail testing",
                        from_email=settings.EMAIL_HOST_USER,
                        to=[email]
                    )
                    message.attach_alternative(html_body, "text/html")
                    message.send(fail_silently=False)
                    # send_mail(email_subject, html_message=message2, settings.EMAIL_HOST_USER, [email],fail_silently=False)

                    # user mail

                    # admin mail

                    if occupation == 'S':
                        occu = 'Student'
                    elif occupation == 'T':
                        occu = 'Teacher'
                    else:
                        occu = occupation_others

                    if gender == 'M':
                        gender_v = 'Male'
                    else:
                        gender_v = 'Female'

                    user_subject = "User Registration Details!!!"
                    user_details = render_to_string('get_user_details_to_admin.html', {
                        'username': uname,
                        'first_name': name,
                        'email': email,
                        'gender': gender_v,
                        'country_code': country_code,
                        'phone_number': phone_number,
                        'occupation': occu,
                        'college': college,
                    })
                    send_mail(user_subject, user_details, settings.EMAIL_HOST_USER, [
                              'janarthanan@aryuenterprises.com'], fail_silently=False)

                    return JsonResponse({"success": True, "redirect": True})

                else:
                    fterrors = dict([(field, [error for error in errors])
                                    for field, errors in form_1.errors.items()])
                    return JsonResponse({"success": False, "errors": fterrors, "step2": True})

        return render(request, "user_registration.html")

    def user_login(request):
        if request.user.is_authenticated:
            return redirect('user_app:user_dash')
        else:
            if request.method == 'POST':
                username = request.POST['username']
                password = request.POST['password']
                remember_me = request.POST.get('remember_me')

                # if username =='' or password =='':
                #     messages.error(request, "Please enter login details")
                #     return redirect('user_app:user_login')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    if user.is_superuser == 'false' and user.is_staff == 'false':
                        messages.error(request, "Invalid Login Details")
                        return redirect('user_app:user_login')

                    if request.POST.get('remember_me'):
                        from datetime import timedelta
                        request.session.set_expiry(timedelta(days=2))
                    else:
                        request.session.set_expiry(settings.DEFAULT_SESSION_VALUE)

                    login(request, user)
                    return redirect('user_app:user_dash')

                else:
                    messages.error(request, "Invalid Login Details")
                    return redirect('user_app:user_login')

        return render(request, "login.html")

    @login_required(login_url='user_app:user_login')
    def user_dash(request):
        users = request.user
        obj = CourseModel.objects.all()
        saved_courses = SavedCourses.objects.filter(user=users)
        courses_saved = [saved_course.course.id for saved_course in saved_courses]
      
        

        purchased_courses = PurchasedCourse.objects.filter(users=users)
        purchased_course_models = [
            purchased_course.courses for purchased_course in purchased_courses]

        latest_course_detail = None
        percentage = 0
        if purchased_course_models:
            latest_course_detail = CourseProgress.objects.filter(user=users)
            if latest_course_detail.count():
                latest_course_detail = latest_course_detail.latest(
                    "watched_date")
                related_modules = purchased_courses.filter(
                    courses=latest_course_detail.course).first().courses.modulemodel_set
                completed_aseessment_count = 0
                for i in related_modules.all():
                    completed_aseessment_count += 1 if i.attemptedassessment_set.filter(
                        user=users).count() > 0 else 0

                progress_count = CourseProgress.objects.filter(
                    user=users, course=latest_course_detail.course).count()+completed_aseessment_count
                total_media_count = latest_course_detail.course.modulemodel_set.filter(status=True).annotate(
                    mmf_count=Count('modulesmediafile')).aggregate(Sum("mmf_count", default=0))
                total_media_count = total_media_count['mmf_count__sum'] + \
                    related_modules.count()
                percentage = round((progress_count/total_media_count)*100)
            else:
                latest_course_detail = None

        return render(request, 'user_dashboard.html', {'course': obj, 'user': request.user, 'purchased_course_models': purchased_course_models, 'latest_course_detail': latest_course_detail, 'percentage': percentage,'saved_courses':saved_courses,'courses_saved':courses_saved})

    @login_required(login_url='user_app:user_login')
    def user_dash_first(request):
        obj = CourseModel.objects.all()
        return render(request, 'user_dash_first.html', {'course': obj, 'user': request.user})

    def user_logout(request):
        logout(request)
        return redirect('user_app:user_login')

    def activate(request, uidb64, token):
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            # login(request, user)
            messages.success(request, "Your account has been activated!")
            return render(request, 'login.html')

        else:
            raise Http404("Poll does not exist")
            # messages.success(request, "user not activate")
            # return redirect('user_app:error')
    # def navbar_view(request):
    #     return render(request, 'navbar.html', {'user': request.user})

    def forgot_password(request):

        return render(request, 'forget_password.html')


# class CustomPasswordResetView(PasswordResetView):
#     form_class = CustomPasswordResetForm
#     template_name = 'forget_password.html'  # Create this template
#     email_template_name = 'password_reset_email.html'  # Create this template
#     success_url = '/password_reset/done/'  # URL to redirect to after password reset request


@login_required(login_url='user_app:user_login')
class UserProfileViews():
    @login_required(login_url='user_app:user_login')
    def user_general_view(request):
        userprofiles = get_object_or_404(UserProfileModel, user=request.user)

        return render(request, 'profile/user_profile_general.html', {'userprofiles': userprofiles})
    
    @login_required(login_url='user_app:user_login')
    def user_edit_profile(request):
        userprofiles = get_object_or_404(UserProfileModel, user=request.user)

        if request.method == 'POST':
            userform = UserProfileEdit(request.POST, request.FILES)
            if userform.is_valid():
                email = request.POST['email']
                first_name = request.POST['first_name']
                last_name = request.POST['last_name']
                profile_img = request.FILES.get('profile_img', None)

                # store - edit profile
                request.user.email = email
                request.user.first_name = first_name
                request.user.last_name = last_name

                request.user.save()

                userprofile = UserProfileModel.objects.get(user=request.user)
                if profile_img:
                    userprofile.profile_img = profile_img
                    userprofile.save()

                return redirect('user_app:user_profile_list')
            else:
                errors = dict([(field, [error for error in errors])
                              for field, errors in userform.errors.items()])
                return render(request, 'profile/user_profile_edit.html', {'form': errors, 'userprofiles': userprofiles})

        return render(request, 'profile/user_profile_edit.html', {'userprofiles': userprofiles})
    
    @login_required(login_url='user_app:user_login')
    def user_profile_media_view(request, file_path):
        # Define the path to the specific folder within MEDIA_ROOT
        specific_folder_path = os.path.join(
            settings.MEDIA_ROOT, 'user_profile_images')

        # Get the full path to the requested file
        requested_file_path = os.path.join(specific_folder_path, file_path)

        # Check if the file exists within the specific folder
        if not os.path.isfile(requested_file_path):
            raise Http404

        # Serve the file
        file = open(requested_file_path, 'rb')
        response = FileResponse(file)
        return response
    
    @login_required(login_url='user_app:user_login')
    def user_password_change_profile(request):
        if request.method == 'POST':
            userformc = UserProfileChangePassword(request.POST)
            print(userformc)
            if userformc.is_valid():
                old_password = request.POST['old_password']
                new_password = request.POST['new_password1']

                if request.user.check_password(old_password):
                    request.user.set_password(new_password)
                    request.user.save()
                    return redirect('user_app:user_profile_list')
            else:
                errors = dict([(field, [error for error in errors])
                              for field, errors in userformc.errors.items()])
                return render(request, 'profile/user_profile_change_password.html', {'form': errors})

        return render(request, 'profile/user_profile_change_password.html')


def error_404(request, exception):
        data = {}
        return render(request,'404.html', data)

@login_required(login_url='user_app:user_login')
class HomePageViews():
    # @staticmethod
    def get_course_objects():
        return CourseModel.objects.all()

    # @staticmethod
    def get_module_objects():
        return ModuleModel.objects.all()

    # @staticmethod
    def get_question_objects():
        return Question.objects.all()

    # @staticmethod
    def get_purchased_objects():
        return PurchasedCourse.objects.all()

    def get_saved_courses():
        return SavedCourses.objects.all()

    # @staticmethod
    def landing_page(request):
        print('test')
        if request.user.is_authenticated:
            return redirect('user_app:user_dash')
        else:
            obj = HomePageViews.get_course_objects()
            return render(request, 'user_home_without_login.html', {'course': obj})

    # @staticmethod
    @login_required(login_url='user_app:user_login')
    def course_detail(request, pk):
        user = request.user
        course = get_object_or_404(CourseModel, pk=pk)
          
        
        offer_courses = Subscription.objects.filter(user=user,course_id=pk)
        sc = [ c.course.id  for c in offer_courses]
        purchased_courses = PurchasedCourse.objects.filter(users=user)
        purchased_course_id = [ pc.courses.id  for pc in purchased_courses]
        # print(purchased_course_id)
        # print(f"sc:{sc}")
        if pk in sc and pk not in purchased_course_id:
            
                offer_course = get_object_or_404(Subscription, user=user, course_id=pk)
                course.price = offer_course.discount

        courses = HomePageViews.get_course_objects()
        modules = course.modulemodel_set.all()
       
        savedcourses = HomePageViews.get_saved_courses()
        bookmark = SavedCourses.objects.filter(user=request.user)


        courses_saved = [saved_course.course.id for saved_course in bookmark]
        
        total_module_days = 0
        total_module_months = 0

        for module in modules:
            duration_days = module.duration_days
            duration_months = module.duration_months
            total_module_days += int(duration_days)
            total_module_months += int(duration_months)

        total_days = total_module_days + (total_module_months*30)

        course_months = total_days // 30

        course_days = total_days - course_months*30

       

        purchased_courses = PurchasedCourse.objects.filter(users=user)
        purchased_course_id = [ pc.courses.id  for pc in purchased_courses]
        print(purchased_course_id)
        
    




        
        # coursest = Subscription.objects.filter(user=user)
        
        filter_courses = Subscription.objects.filter(user=user)
        print(filter_courses)
        if Subscription.objects.filter(user=user).count() > 0 :
    
            # sc = [ c.course.id  for c in coursest]
            # print(sc)
            

            for i in purchased_course_id:
                # print(i)
                filter_courses = filter_courses.exclude(course_id=i)
            # print(f"filter_courses: {filter_courses}")

                
            
                 
       
        return render(request, 'course_details.html', {'course': course, 'courses': courses, 'modules': modules, 'savedcourses': savedcourses, 'course_months': course_months, 'course_days': course_days,'courses_saved':courses_saved ,'filter_courses':filter_courses})

    # @staticmethod
    @login_required(login_url='user_app:user_login')
    def user_learn(request, course_pk):

        users = request.user
        if users.id in PurchasedCourse:
            modules = HomePageViews.get_module_objects()
            purchased_courses = PurchasedCourse.objects.filter(users=users)
            purchased_course_models = [
                purchased_course.courses for purchased_course in purchased_courses]

            selected_course = get_object_or_404(CourseModel, pk=course_pk)

            return render(request, 'user_learning.html', {'modules': modules, 'purchased_course_models': purchased_course_models, 'selected_course': selected_course})
        else:
            return redirect('user_app:courseview')

    #

    # @staticmethod
    @check_purchased_course
    @login_required(login_url='user_app:user_login')
    def user_assesment(request, pk):
        user = request.user
        
        current_watched_date = CourseProgress.objects.filter(user=user, module_id=pk).count()

        

        

        module = get_object_or_404(ModuleModel, pk=pk)
        total_module_material = ModulesMediaFile.objects.filter(module_id=module).count()
        total_watched_date = total_module_material
        if current_watched_date == total_watched_date:
      
        
        # course_pk = module.course_pk.id

            questions = Question.objects.filter(module=module).order_by("?")

            # previous_page_url = request.GET.get('previous_page_url', reverse('user_app:learning', kwargs={'course_pk': course_pk}))

            return render(request, 'user_assesment.html', {'questions': questions, 'module': module})
        else:
            return redirect ('user_app:user_dash')

    # @staticmethod
    @login_required(login_url='user_app:user_login')
    def course_payment(request, pk):
        user=request.user
        course = get_object_or_404(CourseModel, pk=pk)
        offer_courses = Subscription.objects.filter(user=user,course_id=pk)
        sc = [ c.course.id  for c in offer_courses]
        purchased_courses = PurchasedCourse.objects.filter(users=user)
        purchased_course_id = [ pc.courses.id  for pc in purchased_courses]
        # print(purchased_course_id)
        # print(f"sc:{sc}")
        if pk in sc and pk not in purchased_course_id:
            
                offer_course = get_object_or_404(Subscription, user=user, course_id=pk)
                course.price = offer_course.discount
        return render(request, 'payment_details.html', {'course': course})

    # @staticmethod
    def about_us(request):
        return render(request, 'about_us.html')

    # @staticmethod
    # def contact_us(request):
    #     return render(request, 'contact_us.html')

    def contact_us_message(request):
        if request.method == 'POST':
            name = request.POST.get('name')
            email = request.POST.get('email')
            message = request.POST.get('message')

            subject = f"New message from {name}"
            body = f"Name: {name}\nEmail: {email}\n\n{message}"

            body = f"Name: {name}\nEmail: {email}\n\n{message}"
            # settings.DEFAULT_FROM_EMAIL = email
            send_mail(subject, body, settings.EMAIL_HOST_USER,
                      [settings.CONTACT_EMAIL])

            confirmation_subject = "Thank you for contacting us"
            confirmation_body = "Certainly, we've received your message and will reply shortly. Greetings from Medics Academy!"
            send_mail(confirmation_subject, confirmation_body,
                      settings.EMAIL_HOST_USER, [email])

            # Display a success message to the user
            return redirect('user_app:about_us')

        return render(request, 'about_us.html')


@login_required(login_url='user_app:user_login')
class SavedPage:

    # @staticmethod
    def add_to_saved(request, course_id, user_id):
        if request.user.is_authenticated:
            user = get_object_or_404(User, pk=user_id)
            course = get_object_or_404(CourseModel, pk=course_id)

            if not SavedCourses.objects.filter(user=user, course=course).exists():
                SavedCourses.objects.create(user=user, course=course)

        return redirect('user_app:user_dash')

    # @staticmethod
    def remove_from_saved(request, course_id, user_id):
        if request.user.is_authenticated:
            user = get_object_or_404(User, pk=user_id)
            course = get_object_or_404(CourseModel, pk=course_id)

            saved_course = SavedCourses.objects.filter(
                user=user, course=course).first()
            if saved_course:
                saved_course.delete()

        return redirect('user_app:saved_page')

    @login_required
    
    def save_page(request):
        user = request.user  # Get the currently logged-in user
        # Get the SavedCourses objects related to the user
        saved_courses = SavedCourses.objects.filter(user=user)
        for saved_course in saved_courses:
    
           print(saved_course.id, saved_course.course.course_title,saved_course.user.id)

           

        
        


       
        saved_course_models = [
            saved_course.course for saved_course in saved_courses]
        
        saved_course_modelss = [
            saved_course.course.modulemodel_set.all() for saved_course in saved_courses]
       
        

        saved_course_modelss = list(map(lambda saved_course: saved_course.course.modulemodel_set.all(), saved_courses))

        annotated_courses = CourseModel.objects.annotate(module_count=Count('modulemodel'))

        for i in annotated_courses:
            print(f"{i.course_title}:{i.module_count}")

# Aggregate the total duration in days across all modules
        

        
        

      
 
 
         




          
        course_duration = []  
        for course in saved_course_models:
            # print(course)
            course_id =course.id

            course = get_object_or_404(CourseModel, pk=course_id)
            modules = course.modulemodel_set.all()
            total_module_days = 0
            total_module_months = 0
           
            for module in modules:
                duration_days = module.duration_days
                duration_months = module.duration_months
                total_module_days += int(duration_days)
                total_module_months += int(duration_months)

            total_days = total_module_days + (total_module_months * 30)
            course_months = total_days // 30
            course_days = total_days - course_months * 30
           
            course_duration.append({
            'course': course,
            'course_months': course_months,
            'course_days': course_days
        })
        
        # print(course_duration)

        for course in saved_course_models:
            for duration in course_duration:
                # print(duration)
                if duration['course'] == course:
                    course.course_duration_days = duration['course_days']
                    course.course_duration_months = duration['course_months']
                    

        return render(request, 'profile/saved_courses.html', {'saved_course': saved_course_models, 'course_duration': course_duration})

    def saved_check(request, user_id, course_id):
        if request.user.is_authenticated:
            user = get_object_or_404(User, pk=user_id)
            course = get_object_or_404(CourseModel, pk=course_id)

            is_saved = SavedCourses.objects.filter(
                user=user, course=course).exists()

            if is_saved:

                SavedCourses.objects.filter(user=user, course=course).delete()
                success = 0
            else:

                SavedCourses.objects.create(user=user, course=course)
                success = 1

            return JsonResponse({'success': success})
        else:
            return JsonResponse({'error': 'User not authenticated'})


class Search():
    def search_courses(request):
        if request.method == 'POST':
            searched = request.POST['searched']
            courses = CourseModel.objects.filter(
                Q(course_title__icontains=searched))

            return render(request, 'user_search.html', {'searched': searched, 'courses': courses})

        else:

            return render(request, 'user_search.html')


@login_required(login_url='user_app:user_login')
class Purchased():

    # @staticmethod
    def add_to_purchase(request, user_id, course_id):
        if request.user.is_authenticated:
            user = get_object_or_404(User, pk=user_id)
            course = get_object_or_404(CourseModel, pk=course_id)

            offer_courses = Subscription.objects.filter(user=user,course_id=course_id)
            sc = [ c.course.id  for c in offer_courses]
            purchased_courses = PurchasedCourse.objects.filter(users=user)
            purchased_course_id = [ pc.courses.id  for pc in purchased_courses]
         
            if course_id in sc and course_id not in purchased_course_id:
            
                offer_course = get_object_or_404(Subscription, user=user, course_id=course_id)
                course.price = offer_course.discount

            modules = course.modulemodel_set.all()

            total_module_days = 0
            total_module_months = 0

            for module in modules:
                duration_days = module.duration_days
                duration_months = module.duration_months
                total_module_days += int(duration_days)
                total_module_months += int(duration_months)

            total_days = total_module_days + (total_module_months*30)

            course_months = total_days // 30

            course_days = total_days - course_months*30



            is_purchased = False

            if not PurchasedCourse.objects.filter(users=user, courses=course).exists():
                PurchasedCourse.objects.create(users=user, courses=course)
                is_purchased = True

            if is_purchased:

                name = user.first_name
                email = user.email
                course_name = course.course_title
                course_duration = f"{course_months} Months {course_days} Days"
                modules = course.total_modules
                present_date = timezone.now().date()
                purchased_amount = course.price
                print( purchased_amount)
                # message = f"An user purchased a new course\n\nPurchased Details\n\nCourse Name: {course_name}\n\nCourse Duration: {course_duration}\n\nTotal Modules: {modules}\n\nPurchased Date: {present_date}\n\nPurchased Amount: {purchased_amount}"

                subject = f"A user has enrolled in a new course {name}"
                # body = f"Name: {name}\nEmail: {email}\n\n{message}"


                # Render the HTML templates
                message_html = render_to_string('course_purchase_mail.html', {
                    # 'message':message,
                    'name': name,
                    'email': email,
                    'course_name': course_name,
                    'course_duration': course_duration,
                    'modules': modules,
                    'present_date': present_date,
                    'purchased_amount': purchased_amount,

                })
                message_plain = strip_tags(message_html) 

                admin_email = EmailMultiAlternatives(
                subject=subject,
                body=message_plain,
                from_email=settings.EMAIL_HOST_USER,
                to=[settings.CONTACT_EMAIL]
                )

                admin_email.attach_alternative(message_html, "text/html")

                try:
                    admin_email.send()
                except Exception as e:
                    # Handle email failure for admin
                    print(f"Error sending email to admin: {e}")

                confirmation_subject = "Thank you for choosing course"
                confirmation_body = f"Congratulations! You have successfully purchased a course\n\nCourse: {course_name}\n\nCourse Modules: {modules}\n\nPurchased Date: {present_date}"
                
                user_message_html = render_to_string('course_confirm_mail.html', {
                    # 'message':confirmation_body,
                    
                    'email': email,
                    'course_name': course_name,
                    'course_duration': course_duration,
                    'modules': modules,
                    'present_date': present_date,
                   

                })

                user_message_plain = strip_tags(user_message_html) 

                user_email = EmailMultiAlternatives(
                subject=confirmation_subject,
                body=user_message_plain,
                from_email=settings.EMAIL_HOST_USER,
                to=[email]
                )
                user_email.attach_alternative(user_message_html, "text/html")

                try:
                    user_email.send()
                except Exception as e:
                    # Handle email failure for admin
                    print(f"Error sending email to user: {e}")
            return redirect('user_app:user_dash')    

    # @staticmethod
    @login_required
    def purchased_course(request):
        users = request.user

        purchased_courses = PurchasedCourse.objects.filter(users=users)
        purchased_course_models = [
            purchased_course.courses for purchased_course in purchased_courses]
       

        # saved_course_models = [saved_course.course for saved_course in saved_courses]
        
          
        course_duration = []  
        for course in purchased_course_models:
            # print(course)
            course_id =course.id

            course = get_object_or_404(CourseModel, pk=course_id)
            modules = course.modulemodel_set.all()
            total_module_days = 0
            total_module_months = 0
           
            for module in modules:
                duration_days = module.duration_days
                duration_months = module.duration_months
                total_module_days += int(duration_days)
                total_module_months += int(duration_months)

            total_days = total_module_days + (total_module_months * 30)
            course_months = total_days // 30
            course_days = total_days - course_months * 30
           
            course_duration.append({
            'course': course,
            'course_months': course_months,
            'course_days': course_days
        })
        print(course_duration)

        # print(course_duration)

        for course in purchased_course_models:
            print(course)
            for duration in course_duration:
                # print(duration)
                if duration['course'] == course:
                    
                    course.course_duration_days = duration['course_days']
                    course.course_duration_months = duration['course_months']
                  
                        

        return render(request, 'profile/user_my_courses.html', {'purchased_course_models': purchased_course_models,'course_duration': course_duration})

    # @staticmethod
    @login_required(login_url='user_app:user_login')
    def learning(request, course_pk):
        users = request.user

        if not PurchasedCourse.objects.filter(users=users, courses__pk=course_pk).exists():
            return redirect('user_app:user_dash')

        # Retrieve the selected course
        selected_course = get_object_or_404(CourseModel, pk=course_pk)

        # Filter purchased courses for the user
        # purchased_courses = PurchasedCourse.objects.filter(users=users, courses=selected_course)
        purchased_courses = PurchasedCourse.objects.filter(
            users=users, courses=selected_course).first()
        # Get the related modules for the selected course
        related_modules = selected_course.modulemodel_set.order_by(
            'order').all()
        related_modules_pc = purchased_courses.courses.modulemodel_set.order_by(
            'order').all()
        previous_page_url = request.GET.get('previous_page_url', None)

        course_progress_media_id_list = CourseProgress.objects.filter(
            user=users, course=selected_course).values_list('modulemediafile_id', flat=True)
        processed_media_list = []
        at_assessment = []
        a = 1
        last_assessment = 0
        completed_aseessment_count = 0
        for i in related_modules_pc.filter(status=True).order_by('order').all():
            c = CourseProgress.objects.filter(
                user=users, course=selected_course, module=i).count()
            temp_module_dict = {'module_id': i.id}
            k = 1
            last_progress = False
            for j in i.modulesmediafile_set.order_by('order').all():
                temp = {'media_id': j.id}
                if j.id in course_progress_media_id_list:
                    temp['lock'] = False
                    last_progress = True
                elif j.id not in course_progress_media_id_list:
                    if k == 1 and a == 1:
                        temp['lock'] = False
                    elif k > 1 and last_progress == True:
                        temp['lock'] = False
                        last_progress = False
                    elif a > 1 and last_assessment != 0 and k == 1:
                        temp['lock'] = False
                    else:
                        temp['lock'] = True
                else:
                    temp['lock'] = True
                processed_media_list.append(temp)
                k += 1
            last_assessment = i.attemptedassessment_set.filter(
                user=users).count()
            temp_module_dict['count'] = c
            temp_module_dict['acount'] = last_assessment > 0
            at_assessment.append(temp_module_dict)
            completed_aseessment_count += 1 if last_assessment > 0 else 0
            a += 1

        progress_count = CourseProgress.objects.filter(
            user=users, course=selected_course).count()+completed_aseessment_count
        total_media_count = CourseModel.objects.get(pk=course_pk).modulemodel_set.filter(
            status=True).annotate(mmf_count=Count('modulesmediafile')).aggregate(Sum("mmf_count", default=0))
        total_media_count = total_media_count['mmf_count__sum'] + \
            related_modules_pc.filter(status=True).count()
        if total_media_count != 0:
            percentage = str(round((progress_count/total_media_count)*100))
        else:
            percentage = 0
        # print(at_assessment)

        modules = selected_course.modulemodel_set.all()
        module_ids = [module.pk for module in modules]
        attempted_assessments = AttemptedAssessment.objects.filter(
            user_id=users, module_id__in=module_ids)
        total_questions = Question.objects.filter(
            module_id__in=module_ids).count()
        answered_questions = attempted_assessments.filter(
            is_correct=True).count()
        
        module_averages = []

        for module in related_modules:
            total_questions = Question.objects.filter(
                module_id=module.pk).count()
            answered_questions = attempted_assessments.filter(
                module_id=module.pk, is_correct=True).count()
            is_attempted = True if answered_questions > 0 else False
            if total_questions > 0:
                module_average = round(
                    (answered_questions / total_questions) * 100, 2)
            else:
                module_average = 0
            # module.average = module_average  # Assign the average to the module object
            # print(module_averages)
            last_average = None
            re_assessment_avg = ReAssessmentAverage.objects.filter(
                user=users, module=module).last()
            if re_assessment_avg:
                last_average = round(re_assessment_avg.average)
            # print(last_average)
                # re_module_id =re_assessment_avg.module.id
                # print(re_module_id)
                # print(last_average)
            module_averages.append({'module': module, 'is_attempted': is_attempted,
                                   'first_average': module_average, 'last_average': last_average})
            # print(module.pk)
            # Use the last_average variable as needed
        # print(module_averages)

            # for module in related_modules:
            #     if module.id == re_module_id:
            #         if module_average > last_average:

            #             module.average_type = last_average
            #             print(module_average,last_average)
            #         else:
            #             module.average_type = last_average
            #             print(module_average,last_average)

        # create the context dictionary
        context = {
            'related_modules': related_modules,
            'selected_course': selected_course,
            'previous_page_url': previous_page_url,
            'course_progress_percentage': percentage,
            'module_averages': module_averages,
            'processed_media_list': processed_media_list,
            'at_assessment': at_assessment,
            'related_modules_pc': related_modules_pc
        }

        for module in related_modules:
            module.module_averages = [
                avg for avg in module_averages if avg['module'] == module]
            #  print(module.module_averages)

        return render(request, 'user_learning.html', context)

    @login_required(login_url='user_app:user_login')
    def get_popup_question(request):
        if request.method == 'POST':
            question = PopupQuestion.objects.filter(
                module_id=request.POST.get('id')).order_by('?').first()
            data = {}
            if question:
                data['popup_question'] = question.popup_question_text
                choice = question.popupchoice_set.all()
                data['choice'] = []
                for i in choice:
                    if i.is_correct_answer:
                        data['choice'].append(
                            {'id': i.id, 'c': i.popup_choice_text, 'answer': 1})
                    else:
                        data['choice'].append(
                            {'id': i.id, 'c': i.popup_choice_text})
                return JsonResponse({'data': data})
            else:
                return JsonResponse({'no_modules': 1})
        else:
            raise Http404

    @login_required(login_url='user_app:user_login')
    def store_course_progress(request):
        if request.method == 'POST':
            user = request.user
            course = CourseModel.objects.get(pk=request.POST.get('course'))
            module = ModuleModel.objects.get(pk=request.POST.get('module'))
            media = ModulesMediaFile.objects.get(pk=request.POST.get('media'))
            course_progress = CourseProgress.objects.filter(
                user=user, course=course, module=module, modulemediafile=media).count()
            if course_progress == 0:
                CourseProgress.objects.create(
                    user=user, course=course, module=module, modulemediafile=media)
            purchased_courses = PurchasedCourse.objects.filter(
                users=user, courses=course).first()
            related_modules = purchased_courses.courses.modulemodel_set

            completed_aseessment_count = 0
            for i in related_modules.all():
                completed_aseessment_count += 1 if i.attemptedassessment_set.filter(
                    user=user).count() > 0 else 0

            progress_count = CourseProgress.objects.filter(
                user=user, course=course).count()+completed_aseessment_count
            total_media_count = course.modulemodel_set.filter(status=True).annotate(
                mmf_count=Count('modulesmediafile')).aggregate(Sum("mmf_count", default=0))
            total_media_count = total_media_count['mmf_count__sum'] + \
                related_modules.count()
            percentage = round((progress_count/total_media_count)*100)
            lock_assessment = AttemptedAssessment.objects.filter(
                user=user, module=module).count()
            return JsonResponse({'success': 1, 'percentage': percentage, 'lock_assessment': lock_assessment})
        else:
            raise Http404



class ModuleMediaFileView():
    @login_required(login_url='user_app:user_login')
    def module_media_view(request, course_id, file_path):
        if 'HTTP_REFERER' in request.META:
            # print(request.META['REMOTE_USER'])
            user = request.user
            selected_course = get_object_or_404(CourseModel, pk=course_id)
            purchased_courses = PurchasedCourse.objects.filter(
                users=user, courses=selected_course).first()

            if purchased_courses and int(course_id) == purchased_courses.courses.id:
                # Define the path to the specific folder within MEDIA_ROOT
                specific_folder_path = os.path.join(
                    settings.MEDIA_ROOT, 'modules_media')

                # Get the full path to the requested file
                requested_file_path = os.path.join(
                    specific_folder_path, file_path)

                # Check if the file exists within the specific folder
                if not os.path.isfile(requested_file_path):
                    raise Http404

                # Serve the file
                file = open(requested_file_path, 'rb')
                response = FileResponse(file)
                return response
            else:
                raise Http404
        else:
            raise Http404

    @login_required(login_url='user_app:user_login')
    def module_media_signed_view(request, course_id, media_id, signed_value):
        # media_token = request.session.get("material_token", False)
        if request.method == 'POST' and 'HTTP_REFERER' in request.META:
            #     # print(request.META['REMOTE_USER'])
            #     del request.session['material_token']
            user = request.user
            selected_course = get_object_or_404(CourseModel, pk=course_id)
            purchased_courses = PurchasedCourse.objects.filter(
                users=user, courses=selected_course).first()
            from django.core.signing import Signer
            signer = Signer()

            unsigned_media_id = signer.unsign(media_id+':'+signed_value)
            module_file = ModulesMediaFile.objects.get(pk=unsigned_media_id)
            if purchased_courses and int(course_id) == purchased_courses.courses.id:
                if module_file.file_extension == 'url':
                    return JsonResponse({'link': module_file.link})
                elif not os.path.isfile(module_file.uploaded_file.path):
                    raise Http404

                # Serve the file
                else:
                    file = open(module_file.uploaded_file.path, 'rb')
                    response = FileResponse(file)
                    return response
            else:
                raise Http404
        else:
            raise Http404


# def attempted_assessment(request, user_id, module_id, question_id, choice_id):

#     user = User.objects.get(pk=user_id)
#     module_instance = ModuleModel.objects.get(pk=module_id)
#     question_instance = Question.objects.get(pk=question_id)
#     selected_choice = Choice.objects.get(pk=choice_id)
#     correct_question_answer = Question.objects.filter(module=question_instance.module, choice__is_correct_answer=True).first()

#     # if selected_choice.is_correct_answer  == correct_question_answer:
#     #         is_correct = True
#     # else:
#     #         is_correct = False


#     is_correct = (selected_choice.is_correct_answer  == correct_question_answer)
#     if module_instance in AttemptedAssessment.objects.all():

#         ReAssessment.objects.create( user=user, module=module_instance,question=question_instance,
#                                             selected_choice=selected_choice, is_correct=is_correct)
#     else:
#         AttemptedAssessment.objects.create( user=user, module=module_instance,question=question_instance,
#                                             selected_choice=selected_choice, is_correct=is_correct)


#     return redirect('assessment_success')

@login_required(login_url='user_app:user_login')
def assessment_submit(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            user = request.user
            module_id = request.POST.get('module')

            reassessmentFlag = False
            if AttemptedAssessment.objects.filter(user=request.user, module=module_id).exists():
                reassessmentFlag = True

            total_questions = Question.objects.filter(
                module_id=module_id).count()
            module_instance = ModuleModel.objects.get(pk=module_id)
            course_id = module_instance.course

            answered_questions = 0
            for i in request.POST:
                if i == 'csrfmiddlewaretoken' or i == 'module':
                    continue

                question_id, choice_id = request.POST.get(i).split('_')
                question_instance = Question.objects.get(pk=question_id)
                selected_choice = Choice.objects.get(pk=choice_id)

                correct_question_answer = Choice.objects.filter(
                    question=question_instance, is_correct_answer=True).get()

                is_correct = True if selected_choice.id == correct_question_answer.id else False
                if is_correct:
                    answered_questions += 1

                if not reassessmentFlag:
                    AttemptedAssessment.objects.create(user=user, module=module_instance, question=question_instance,
                                                       selected_choice=selected_choice, is_correct=is_correct)

            average = answered_questions / total_questions * 100
            rounded_average = round(average)
            print(rounded_average)

            if reassessmentFlag:
                ReAssessmentAverage.objects.create(
                    user=user, course=course_id, module=module_instance, average=rounded_average)

            return JsonResponse({'success': 1})
        else:
            raise Http404
    else:
        return JsonResponse({'login': 0})








# def course_duration(request,course_id):
#      selected_course = get_object_or_404(CourseModel, pk=course_id)
#      duration_days = selected_course.modulemodel_set.get(duration_days)


# def view_average_mark(request, user_id, module_id):
#     # Calculate the average mark for a specific user and module
#     attempted_assessments = AttemptedAssessment.objects.filter(user_id=user_id, module_id=module_id)
#     total_questions = Question.objects.filter(module_id=module_id).count()
#     answered_questions = attempted_assessments.filter(is_correct=True).count()
#     average = answered_questions / total_questions * 100


#     print(f"Average Mark: {average}%")


#     return HttpResponse(f"{average}% Average Mark Calculated and Printed in Terminal")


# @staticmethod
#     @login_required(login_url='user_app:user_login')
#     def user_assesment(request, pk):
#         module = get_object_or_404(ModuleModel, pk=pk)
#         questions = Question.objects.filter(module=module)
#         paginator = Paginator(questions,8)
#         page_num = request.GET.get("page")

#         page_obj =paginator.get_page(page_num)


#         return render(request, 'user_assesment.html', {'questions': questions, 'module': module,"page_obj": page_obj})

# class HomePageViews():

#     def landing_page(request):
#         obj = CourseModel.objects.all()
#         return render(request, 'user_home_without_login.html' ,{'course':obj})


#     def user_dash(request):
#         return render(request, 'user_dashboard.html' ,{'course':obj})

# reduce code line repeat unwanted
# obj = CourseModel.objects.all() this i need for both fuctions
