from typing import Any,Union
from django.contrib import admin, messages
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http.response import HttpResponse
from django.template.response import TemplateResponse
from django.urls import path
from django.conf import settings
from django.contrib.auth.models import Group, User, Permission
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from .models import CourseModel, ModuleModel, ModulesMediaFile, Question, Choice, PopupQuestion, PopupChoice, Subscription
from django.shortcuts import redirect
from .views import StaffProfileViews
from django.urls import reverse_lazy, reverse
from courses.forms import ModuleModelAdminForm, QuestionAdminForm, CustomUserAdminForm, CustomUserChangeAdminForm, ImportQuestionForm, PopupQuestionAdminForm
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.utils.html import escape
from django.db import transaction
from django.db.models import Count,QuerySet
from django.utils import timezone
import csv, datetime
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from zoneinfo import ZoneInfo

from django.db import models

class MedicsAdminSite(admin.AdminSite):
    site_header = "Medics Academy Administration"
    login_template = 'admin/login.html'  

    index_template = 'admin/dashboard.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_login_view = path('login/', CustomAdminLoginView.as_view(), name='login')
        urls.insert(0, custom_login_view)

        custom_password_view = path('password_change/', CustomAdminPasswordChangeView.as_view(), name='admin_password_change')
        urls.insert(0, custom_password_view)

        staff_profile_view = path('general_profile/', self.admin_view(StaffProfileViews.general_view), name='staff_profile_general_view')
        urls.insert(0, staff_profile_view)

        staff_profile_edit = path('general_profile_edit/', self.admin_view(StaffProfileViews.edit_profile_view), name='staff_profile_general_edit')
        urls.insert(0, staff_profile_edit)

        courses_url = path('courses/', self.admin_view(StaffProfileViews.error_404))
        urls.insert(0, courses_url)

        admin_slash = path('admin/', self.admin_view(StaffProfileViews.error_404))
        urls.insert(0, admin_slash)

        return urls
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        course_count = CourseModel.objects.count()
        
        no_of_students = User.objects.filter(is_superuser=False,is_staff=False).count()
        
        user_model_query = User.objects.annotate(pcourse_count=Count('purchasedcourse'))
        conversion_students = user_model_query.filter(is_superuser=False,is_staff=False,pcourse_count__gt=0).count()
        
        if not request.GET.get('non_active_students') or request.GET.get('non_active_students') == 'recent':
            one_week_ago = timezone.now() - datetime.timedelta(weeks=1)
            user_list = user_model_query.filter(is_superuser=False,is_staff=False,pcourse_count__gt=0,last_login__week=one_week_ago.isocalendar()[1], last_login__year=one_week_ago.year).all()
        elif request.GET.get('non_active_students') == 'last_month':
            one_month_ago = timezone.now() - datetime.timedelta(days=30)
            user_list = user_model_query.filter(is_superuser=False,is_staff=False,pcourse_count__gt=0,last_login__month=one_month_ago.month,last_login__year=one_month_ago.year).all()
        else:
            user_list = []
            

        extra_context['data'] = {'name': request.user.first_name+' '+request.user.last_name if request.user.first_name!='' else request.user.username, 'course_count': course_count, 'no_of_students': no_of_students, 'conversion_students': conversion_students, 'user_list': user_list}
        return super(MedicsAdminSite, self).index(request, extra_context)

class CustomAdminLoginView(LoginView):
    template_name = 'admin/login.html'

    redirect_authenticated_user = True

    def form_valid(self, form):
        # Perform the default login logic
        response = super().form_valid(form)
        
        # Add your additional functionality after successful authentication
        # For example, you can log the admin login activity here
        if self.request.POST.get('remember_me'):
            self.request.session.set_expiry(172800)
        else:
            self.request.session.set_expiry(settings.DEFAULT_SESSION_VALUE)

        return response
    
    def get_redirect_url(self):
        if 'next' in self.request.POST:
            return self.request.POST['next']
        else:
            if(self.request.user.is_authenticated and self.request.user.is_staff):
                return '/admin'
            else:
                return '/login'
        
class CustomAdminPasswordChangeView(PasswordChangeView):
    template_name = 'admin/profile_change_password.html'
    success_url = reverse_lazy('admin:staff_profile_general_view')
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been successfully changed.')
        return super().form_valid(form)

class CourseModelAdmin(admin.ModelAdmin):

    # Customize the list display
    list_display = ('course_title', 'status', 'created_at')

    # readonly_fields = ('course_name', 'status', 'created_at')

    # Customize the search functionality
    search_fields = ['course_title']

    # Customize filters
    list_filter = ('course_title','status','created_at')

    list_per_page = 10

    add_form_template = 'admin/courses/coursemodel_add_form.html'

    change_list_template = 'admin/courses/coursemodel_change_list.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        if 'month' in request.GET:
            modified_get = request.GET.copy()
            extra_context['month_query'] = modified_get['month']
            del modified_get['month']
            if 'created_at__gte' in modified_get:
                created_at_gte = modified_get['created_at__gte'].split(' ')
                created_at_lte = modified_get['created_at__lte'].split(' ')
                extra_context['created_at_query'] = created_at_gte[0]+ ' - ' +created_at_lte[0]
            request.GET = modified_get
        return super().changelist_view(request, extra_context)

    def view_course(self, request, object_id):
        self.change_form_template = 'admin/courses/coursemodel_view_course.html'
        return self.change_view(request, object_id)
    
    def edit_course(self, request, object_id):
        self.change_form_template = 'admin/courses/coursemodel_edit_course.html'
        return self.change_view(request, object_id)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<object_id>/view_course/', self.view_course, name='view_course'),
            path('<object_id>/edit_course/', self.edit_course, name='edit_course'),
            path('export_as_csv/', self.export_as_csv, name='course_export_as_csv')
        ]
        return custom_urls + urls
    
    def message_user(self, request: HttpRequest, message: str, level: Union[int, str] = ..., extra_tags: str = ..., fail_silently: bool = ...) -> None:
        if level == messages.SUCCESS:
            pass
        elif level == messages.WARNING or level == messages.ERROR:
            return super().message_user(request, message, level, extra_tags, fail_silently)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            messages.success(request, 'Course was successfully updated.')
        else:
            messages.success(request, 'Course was successfully added.')
    
    def delete_model(self, request, obj):
        super().delete_model(request,obj)
        messages.success(request, 'Course was successfully deleted.')

    def delete_view(self, request: HttpRequest, object_id: str, extra_context: None = ...) -> Any:
        try:
            return super().delete_view(request, object_id, extra_context)
        except Exception as e:
            message = "Cannot delete the course because it is associated with a module. You can only delete the course by deleting the associated module."
            self.message_user(request, message, level=messages.WARNING, extra_tags='warning')
            return redirect('admin:courses_coursemodel_changelist')

    def export_as_csv(self, request):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        
        course = CourseModel.objects.all().order_by('id')

        writer.writerow(field_names)
        for obj in course:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response


class ModuleModelAdmin(admin.ModelAdmin):
    form = ModuleModelAdminForm
    add_form_template = 'admin/courses/modulemodel_add_form.html'

    def message_user(self, request: HttpRequest, message: str, level: Union[int, str] = ..., extra_tags: str = ..., fail_silently: bool = ...) -> None:
        if level == messages.SUCCESS:
            pass
        elif level == messages.WARNING or level == messages.ERROR:
            extra_tags = ''
            return super().message_user(request, message, level, extra_tags, fail_silently)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        rpath = request.path.split('/')
        try:
            if(rpath[5] == 'list_course_modules'):
                course_id = rpath[4]
                if course_id is not None and course_id != '':
                    return super().get_queryset(request).filter(course=course_id).order_by('order')
        except IndexError:
            return super().get_queryset(request)
        return super().get_queryset(request)
    
    def changelist_view(self, request, extra_context=None):
        if(request.path_info == '/admin/courses/modulemodel/'):
            raise Http404('Page not found!')
        return super().changelist_view(request, extra_context)

    def list_course_modules(self, request, object_id):
        self.list_per_page = 10
        self.change_list_template = 'admin/courses/modulemodel_list_course_modules.html'
        course = CourseModel.objects.get(pk=object_id)
        return self.changelist_view(request, extra_context={'course': course})
    
    def edit_module(self, request, object_id):
        self.change_form_template = 'admin/courses/modulemodel_edit_module.html'
        return self.change_view(request, object_id)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/list_course_modules/', self.list_course_modules, name='list_course_modules'),
            path('<object_id>/edit_module/', self.edit_module, name='edit_module'),
            path('export_as_csv/', self.export_as_csv, name='module_export_as_csv')
        ]
        return custom_urls + urls

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # print(request.POST)

        if(request.POST.get('video_file')):
            video_file_num = request.POST.get('video_file').split(',')
        else:
            video_file_num = []
        if(request.POST.get('audio_file')):
            audio_file_num = request.POST.get('audio_file').split(',')
        else:
            audio_file_num = []
        if(request.POST.get('document_file')):
            document_file_num = request.POST.get('document_file').split(',')
        else:
            document_file_num = []
        # for i in range(int(request.POST.get('file_num'))):
        for i in request.POST.get('file_num').split(','):
            if i != '':
                l = f'mlink_{i}'
                # print(form.cleaned_data)

                file_link = request.POST.get(l)
                file_data = form.cleaned_data.get(f'uploaded_file_{i}')
                file_order = form.cleaned_data.get(f'forder_{i}')
                

                # print(file_link)
            
                # print(file_order)
                # print(file_data)
                if i in video_file_num:
                    file_type = 'Video'
                if i in audio_file_num:
                    file_type = 'Audio'
                if i in document_file_num:
                    file_type = 'Document'
                if file_data != None:
                    file_extension = file_data.name.split('.')[-1]
                else:
                    file_extension = "url"    

                ModulesMediaFile.objects.create(module=obj, uploaded_file=file_data, order=file_order, file_extension=file_extension, file_type=file_type,link=file_link )
        for j in request.POST.get('popup_qt_num').split(','):
            if j != '':
                popup_question_obj = PopupQuestion.objects.create(popup_show_time=form.cleaned_data.get(f'popup_show_time_{j}'),module=obj,popup_question_text=form.cleaned_data.get(f'popup_question_{j}'))
                choice_data = request.POST.getlist(f'choices_{j}')
                flag = False
                for choice in choice_data:
                    correct_answer = False
                    if form.cleaned_data.get(f'answer_{j}') == choice and flag == False:
                        correct_answer = True
                        flag = True
                    PopupChoice.objects.create(popup_question=popup_question_obj, popup_choice_text=choice, is_correct_answer=correct_answer)
        # uploaded_file_data = form.cleaned_data.get('uploaded_file')
        # if uploaded_file_data:
        #     for file_data in uploaded_file_data:
        #         ModulesMediaFile.objects.create(module=obj, uploaded_file=file_data)
        if change:
            messages.success(request, 'Module was successfully updated.')
        else:
            messages.success(request, 'Module was successfully added.')
    
    def delete_model(self, request, obj):
        super().delete_model(request,obj)
        messages.success(request, 'Module was successfully deleted.')
    
    def response_add(self, request, obj):
        response = super().response_add(request, obj)
        if "_continue" not in request.POST and "_addanother" not in request.POST:
            # return HttpResponseRedirect(reverse('admin:list_course_modules',args=str(obj.course.id)))
            return response

        return response

    def response_change(self, request, obj):
        response = super().response_change(request, obj)
        if "_continue" not in request.POST and "_addanother" not in request.POST:
            return HttpResponseRedirect(reverse('admin:list_course_modules',args=[str(obj.course.id)]))

        return response
    
    def response_delete(self, request, obj_display, obj_id):
        response = super().response_delete(request, obj_display, obj_id)
        redirect_url = reverse('admin:list_course_modules', args=[request.POST.get('course_id')])
        if response.status_code == 302:
            return HttpResponseRedirect(redirect_url)
        return response
    
    def add_view(self, request, form_url='', extra_context=None):
        if request.GET and request.GET.get('course') != '':
            course = CourseModel.objects.get(pk=request.GET.get('course'))
            extra_context = extra_context or {}
            extra_context['course'] = course
            response = super().add_view(request, form_url, extra_context)
            return response
        else:
            raise Http404('Page not found!')

    def export_as_csv(self, request):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        
        course_id = request.GET.get('course')

        module = ModuleModel.objects.filter(course=course_id).order_by('id')

        writer.writerow(field_names)
        for obj in module:
            row = []
            for field in field_names:
                if field == 'course':
                    row.append(getattr(obj, field).course_title)
                else:
                    row.append(getattr(obj, field))
            row = writer.writerow(row)

        return response
    
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if request.method == 'POST':
            response = super().changeform_view(request, object_id, form_url, extra_context)
            if isinstance(response, HttpResponseRedirect):
                return JsonResponse({'success': 1}, status=200)
            else:
                context_data = response.context_data
                form = context_data.get('adminform').form
                if form.errors and len(form.errors):
                    return JsonResponse({'form': form.errors}, status=422)
                else:
                    return JsonResponse({'success': 1}, status=200)
            # if form.is_valid()
            # object = self.get_object(request, object_id) or None
            # form = ModuleModelAdminForm(data=request.POST, files=request.FILES, instance=object)
            # if form.is_valid():
            #     super().changeform_view(request, object_id, form_url, extra_context)
            #     return JsonResponse({'success': 1}, status=200)
            # else:
            #     return JsonResponse({'form': form.errors}, status=422)
        return super().changeform_view(request, object_id, form_url, extra_context)
    
    def get_form(self, request, obj=None, **kwargs):
        if request.method == 'POST':
            kwargs["form"] = ModuleModelAdminForm
        form = super().get_form(request, obj, **kwargs)
        return form

class ModulesMediaFileAdmin(admin.ModelAdmin):
    def delete_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, object_id)
        if obj is None:
            # Object not found, return a JSON error response
            return JsonResponse({'error': 'Object not found'}, status=404)

        # Store the object's string representation for the response message
        obj_str = escape(str(obj.uploaded_file.name))
        obj.delete()
        success_message = f'{obj_str} has been deleted.'

        response_data = {'success': success_message}
        return JsonResponse(response_data)

class PopupQuestionAdmin(admin.ModelAdmin):
    form = PopupQuestionAdminForm
    add_form_template = 'admin/courses/popupquestionmodel_add_form.html'

    def message_user(self, request: HttpRequest, message: str, level: Union[int, str] = ..., extra_tags: str = ..., fail_silently: bool = ...) -> None:
        if level == messages.SUCCESS:
            pass
        elif level == messages.WARNING or level == messages.ERROR:
            extra_tags = ''
            return super().message_user(request, message, level, extra_tags, fail_silently)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/list_module_popup_question/', self.list_module_popup_question, name='list_module_popup_question'),
            path('<object_id>/edit_popup_question/', self.edit_popup_question, name='edit_popup_question'),
            path('<object_id>/import_module_popup_questions/', self.import_module_popup_questions, name='import_module_popup_questions')
        ]
        return custom_urls + urls
    
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        rpath = request.path.split('/')
        try:
            if(rpath[5] == 'list_module_popup_question'):
                module_id = rpath[4]
                if module_id is not None and module_id != '':
                    return super().get_queryset(request).filter(module=module_id).order_by('created_at')
        except IndexError:
            return super().get_queryset(request)
        return super().get_queryset(request)
    
    def changelist_view(self, request, extra_context=None):
        if(request.path_info == '/admin/courses/popupquestion/'):
            raise Http404('Page not found!')
        extra_context = extra_context or {}
        extra_context['clink'] = 'list_module_questions'
        return super().changelist_view(request, extra_context)
    
    def list_module_popup_question(self, request, object_id):
        self.list_per_page = 10
        self.change_list_template = 'admin/courses/popupquestionmodel_list_module_questions.html'
        module = ModuleModel.objects.get(pk=object_id)
        return self.changelist_view(request, extra_context={'module': module})
    
    def edit_popup_question(self, request, object_id):
        self.change_form_template = 'admin/courses/popupquestionmodel_edit_question.html'
        return self.change_view(request, object_id)
    
    def import_module_popup_questions(self, request, object_id):
        if request.method == 'POST':
            f = ImportQuestionForm(request.POST, request.FILES)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        module = ModuleModel.objects.get(pk=object_id)
                        file = request.FILES['csvfile'] 
                        decoded_file = file.read().decode('utf-8').splitlines()
                        reader = csv.DictReader(decoded_file)
                        for row in reader:
                            question_obj = PopupQuestion.objects.create(module=module,popup_question_text=row['Q'])
                            answer = f"C{row['A']}"
                            flag = False
                            correct_answer = False
                            for i in range(1, 5):
                                choice = f"C{i}"
                                if answer == choice and flag == False:
                                    correct_answer = True
                                    flag = True
                                if choice in row and row[choice] != '':
                                    PopupChoice.objects.create(popup_question=question_obj, popup_choice_text=row[choice], is_correct_answer=correct_answer)
                                    correct_answer = False
                        LogEntry.objects.log_action(
                            user_id=request.user.id,
                            content_type_id=ContentType.objects.get_for_model(module).pk,
                            object_repr=str(module),
                            object_id=object_id,
                            change_message="Popup Questions are imported",
                            action_flag=ADDITION
                        )
                        messages.success(request, 'Popup Questions are successfully imported!!')
                        response_data = {'success': 1}
                except Exception as err:
                    errors = { 'csvfile' : [str(err)]}
                    return JsonResponse({'form': errors}, status=422)
            else:
                return JsonResponse({'form': f.errors}, status=422)
            return JsonResponse(response_data)
        else:
            raise Http404('Page not found!')
    
    def add_view(self, request, form_url='', extra_context=None):
        if request.GET and request.GET.get('module') != '':
            module = ModuleModel.objects.get(pk=request.GET.get('module'))
            extra_context = extra_context or {}
            extra_context['module'] = module
            response = super().add_view(request, form_url, extra_context)
            return response
        else:
            raise Http404('Page not found!')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            PopupChoice.objects.filter(popup_question=obj).delete()
        choice_data = request.POST.getlist('choices')
        flag = False
        for choice in choice_data:
            correct_answer = False
            if form.cleaned_data.get('answer') == choice and flag == False:
                correct_answer = True
                flag = True
            PopupChoice.objects.create(popup_question=obj, popup_choice_text=choice, is_correct_answer=correct_answer)
        if change:
            messages.success(request, 'Popup Question was successfully updated.')
        else:
            messages.success(request, 'Popup Question was successfully added.')

    def response_add(self, request, obj):
        response = super().response_add(request, obj)
        if "_continue" not in request.POST and "_addanother" not in request.POST:
            return HttpResponseRedirect(reverse('admin:list_module_popup_question',args=[str(obj.module.id)]))
        return response
    
    def response_change(self, request, obj):
        response = super().response_change(request, obj)
        if "_continue" not in request.POST and "_addanother" not in request.POST:
            return HttpResponseRedirect(reverse('admin:list_module_popup_question',args=[str(obj.module.id)]))

        return response
    
    def response_delete(self, request, obj_display, obj_id):
        if request.method == 'POST':
            module_id = request.POST['module']
            response = super().response_delete(request, obj_display, obj_id)
            return HttpResponseRedirect(reverse('admin:list_module_popup_question',args=[str(module_id)]))
        else:
            return super().response_delete(request, obj_display, obj_id)
    
    def delete_model(self, request, obj):
        super().delete_model(request,obj)
        messages.success(request, 'Popup Question was successfully deleted.')

    # def delete_view(self, request, object_id, extra_context=None):
    #     obj = self.get_object(request, object_id)
    #     if obj is None:
    #         # Object not found, return a JSON error response
    #         return JsonResponse({'error': 'Object not found'}, status=404)

    #     # Store the object's string representation for the response message
    #     obj.delete()
    #     success_message = 'Popup Question and its choices are deleted.'

    #     response_data = {'success': success_message}
    #     return JsonResponse(response_data)

class QuestionAdmin(admin.ModelAdmin):
    form = QuestionAdminForm
    add_form_template = 'admin/courses/questionmodel_add_form.html'

    def message_user(self, request: HttpRequest, message: str, level: Union[int, str] = ..., extra_tags: str = ..., fail_silently: bool = ...) -> None:
        if level == messages.SUCCESS:
            pass
        elif level == messages.WARNING or level == messages.ERROR:
            extra_tags = ''
            return super().message_user(request, message, level, extra_tags, fail_silently)
        
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        rpath = request.path.split('/')
        try:
            if(rpath[5] == 'list_module_questions'):
                module_id = rpath[4]
                if module_id is not None and module_id != '':
                    return super().get_queryset(request).filter(module=module_id).order_by('created_at')
        except IndexError:
            return super().get_queryset(request)
        return super().get_queryset(request)
    
    def changelist_view(self, request, extra_context=None):
        if(request.path_info == '/admin/courses/question/'):
            raise Http404('Page not found!')
        extra_context = extra_context or {}
        extra_context['clink'] = 'list_module_questions'
        return super().changelist_view(request, extra_context)
        
    def list_module_questions(self, request, object_id):
        self.list_per_page = 10
        self.change_list_template = 'admin/courses/questionmodel_list_module_questions.html'
        module = ModuleModel.objects.get(pk=object_id)
        return self.changelist_view(request, extra_context={'module': module})
    
    def edit_question(self, request, object_id):
        self.change_form_template = 'admin/courses/questionmodel_edit_question.html'
        return self.change_view(request, object_id)
    
    def import_module_questions(self, request, object_id):
        if request.method == 'POST':
            f = ImportQuestionForm(request.POST, request.FILES)
            if f.is_valid():
                try:
                    with transaction.atomic():
                        module = ModuleModel.objects.get(pk=object_id)
                        file = request.FILES['csvfile'] 
                        decoded_file = file.read().decode('utf-8').splitlines()
                        reader = csv.DictReader(decoded_file)
                        for row in reader:
                            question_obj = Question.objects.create(module=module,question_text=row['Q'])
                            answer = f"C{row['A']}"
                            flag = False
                            correct_answer = False
                            for i in range(1, 5):
                                choice = f"C{i}"
                                if answer == choice and flag == False:
                                    correct_answer = True
                                    flag = True
                                if choice in row and row[choice] != '':
                                    Choice.objects.create(question=question_obj, choice_text=row[choice], is_correct_answer=correct_answer)
                                    correct_answer = False
                        LogEntry.objects.log_action(
                            user_id=request.user.id,
                            content_type_id=ContentType.objects.get_for_model(module).pk,
                            object_repr=str(module),
                            object_id=object_id,
                            change_message="Assessment Questions are imported",
                            action_flag=ADDITION
                        )
                        messages.success(request, 'Questions are successfully imported!!')
                        response_data = {'success': 1}
                except Exception as err:
                    errors = { 'csvfile' : [str(err)]}
                    return JsonResponse({'form': errors}, status=422)
            else:
                return JsonResponse({'form': f.errors}, status=422)
            return JsonResponse(response_data)
        else:
            raise Http404('Page not found!')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/list_module_questions/', self.list_module_questions, name='list_module_questions'),
            path('<object_id>/edit_question/', self.edit_question, name='edit_question'),
            path('<object_id>/import_module_questions/', self.import_module_questions, name='import_module_questions')
        ]
        return custom_urls + urls

    def add_view(self, request, form_url='', extra_context=None):
        if request.GET and request.GET.get('module') != '':
            module = ModuleModel.objects.get(pk=request.GET.get('module'))
            extra_context = extra_context or {}
            extra_context['module'] = module
            response = super().add_view(request, form_url, extra_context)
            return response
        else:
            raise Http404('Page not found!')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            Choice.objects.filter(question=obj).delete()
        choice_data = request.POST.getlist('choices')
        flag = False
        for choice in choice_data:
            correct_answer = False
            if form.cleaned_data.get('answer') == choice and flag == False:
                correct_answer = True
                flag = True
            Choice.objects.create(question=obj, choice_text=choice, is_correct_answer=correct_answer)
        if change:
            messages.success(request, 'Question was successfully updated.')
        else:
            messages.success(request, 'Question was successfully added.')

    def response_add(self, request, obj):
        response = super().response_add(request, obj)
        if "_continue" not in request.POST and "_addanother" not in request.POST:
            return HttpResponseRedirect(reverse('admin:list_module_questions',args=[str(obj.module.id)]))
        return response
    
    def response_change(self, request, obj):
        response = super().response_change(request, obj)
        if "_continue" not in request.POST and "_addanother" not in request.POST:
            return HttpResponseRedirect(reverse('admin:list_module_questions',args=[str(obj.module.id)]))

        return response
    
    def response_delete(self, request, obj_display, obj_id):
        if request.method == 'POST':
            module_id = request.POST['module']
            response = super().response_delete(request, obj_display, obj_id)
            return HttpResponseRedirect(reverse('admin:list_module_questions',args=[str(module_id)]))
        else:
            return super().response_delete(request, obj_display, obj_id)
    
    def delete_model(self, request, obj):
        super().delete_model(request,obj)
        messages.success(request, 'Question was successfully deleted.')

class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserAdminForm
    add_form_template = 'admin/courses/usermodel_add_form.html'

    # Customize the search functionality
    search_fields = ['username','email']

    def message_user(self, request: HttpRequest, message: str, level: Union[int, str] = ..., extra_tags: str = ..., fail_silently: bool = ...) -> None:
        if level == messages.SUCCESS:
            pass
        elif level == messages.WARNING or level == messages.ERROR:
            extra_tags = ''
            return super().message_user(request, message, level, extra_tags, fail_silently)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        rpath = request.path.split('/')
        if rpath[4] == 'list_admin_users':
            return super().get_queryset(request).filter(is_staff=True, is_superuser=False)
        elif rpath[4] == 'list_student_users':
            return super().get_queryset(request).filter(is_staff=False, is_superuser=False)
        return super().get_queryset(request).filter(is_staff=True, is_superuser=False)

    def changelist_view(self, request, extra_context=None):
        if(request.path_info == '/admin/auth/user/'):
            raise Http404('Page not found!')
        extra_context = extra_context or {}
        rpath = request.path.split('/')
        if rpath[4] == 'list_student_users' and 'month' in request.GET:
            modified_get = request.GET.copy()
            extra_context['month_query'] = modified_get['month']
            del modified_get['month']
            if 'date_joined__gte' in modified_get:
                date_joined_gte = modified_get['date_joined__gte'].split(' ')
                date_joined_lte = modified_get['date_joined__lte'].split(' ')
                extra_context['date_joined_query'] = date_joined_gte[0]+ ' - ' +date_joined_lte[0]
            request.GET = modified_get
        return super().changelist_view(request, extra_context)

    @method_decorator(permission_required('auth.change_user',raise_exception=True))        
    def list_admin_users(self, request):
        self.list_per_page = 10
        self.change_list_template = 'admin/courses/usermodel_list_admin_users.html'
        if request.method == 'POST' and request.user.has_perm('auth.change_user'):
            c_user = User.objects.get(pk=int(request.POST.get('user_id')))
            if request.POST.get('is_active') is None:
                c_user.is_active = False
            else:
                c_user.is_active = True
            c_user.save()
            messages.success(request, 'User status was successfully updated.')
            return HttpResponseRedirect(reverse('admin:list_admin_users'))
        return self.changelist_view(request)

    @method_decorator(permission_required('auth.change_user',raise_exception=True))
    def edit_user(self, request, object_id):
        self.form = CustomUserChangeAdminForm
        self.change_form_template = 'admin/courses/usermodel_edit_user.html'
        permissions = Permission.objects.filter(content_type__app_label='courses').order_by('id')
        user_permission = Permission.objects.filter(content_type__model='user').order_by('id')
        extra_context = {}
        extra_context['permissions'] = permissions | user_permission
        return self.change_view(request, object_id,extra_context=extra_context)
    
    @method_decorator(permission_required('auth.view_user',raise_exception=True))
    def list_student_users(self, request, extra_context = None):
        self.search_fields = ['username','email', 'first_name', 'last_name']
        self.list_filter = ['date_joined']
        self.list_per_page = 10
        self.change_list_template = 'admin/student_list.html'
        extra_context = extra_context or {}
        return self.changelist_view(request, extra_context)
    
    @method_decorator(permission_required('auth.view_user',raise_exception=True))
    def export_as_csv(self, request):
        field_names = ['Username', 'First name', 'Last name', 'Email', 'Total Purchased Courses', 'Duration','Status', 'Date of joining']
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format('students_list')
        writer = csv.writer(response)
        
        users = User.objects.filter(is_staff=False, is_superuser=False).all().order_by('id')

        writer.writerow(field_names)
        for obj in users:
            course_ids = [pcourse.courses_id for pcourse in obj.purchasedcourse_set.all()]
            months = 0
            days = 0
            for i in course_ids:
                modules = CourseModel.objects.get(pk=i).modulemodel_set.all()
                for j in modules:
                    months += int(j.duration_months)
                    days += int(j.duration_days)
            duration = str(months)+ ' months '+ str(days) + ' days'
            status = 'Active' if obj.is_active else 'Inactive'
            date_joined = obj.date_joined
            ak_tz = timezone.activate(zoneinfo.ZoneInfo('Asia/Kolkata'))
            date_joined = date_joined.astimezone(ak_tz).strftime("%Y-%m-%d %I:%M %p")

            row = [
                obj.username,
                obj.first_name,
                obj.last_name,
                obj.email,
                obj.purchasedcourse_set.count(),
                duration,
                status,
                date_joined
            ]
            row = writer.writerow(row)

        return response

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('list_admin_users/', self.list_admin_users, name='list_admin_users'),
            path('<object_id>/edit_user/', self.edit_user, name='edit_user'),
            path('list_student_users/', self.list_student_users, name='student_user_list'),
            path('export_as_csv/', self.export_as_csv, name='student_list_export_as_csv')
        ]
        return custom_urls + urls
    
    def add_view(self, request, form_url='', extra_context=None):
        permissions = Permission.objects.filter(content_type__app_label='courses').order_by('id')
        user_permission = Permission.objects.filter(content_type__model='user').order_by('id')
        extra_context = extra_context or {}
        extra_context['permissions'] = permissions | user_permission
        response = super().add_view(request, form_url, extra_context)
        return response
    
    def response_add(self, request, obj):
        response = super().response_add(request, obj)
        if "_continue" not in request.POST and "_addanother" not in request.POST:
            return HttpResponseRedirect(reverse('admin:list_admin_users'))
        return response
    
    def response_change(self, request, obj):
        response = super().response_change(request, obj)
        if "_continue" not in request.POST and "_addanother" not in request.POST:
            return HttpResponseRedirect(reverse('admin:list_admin_users'))

        return response
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            messages.success(request, 'User was successfully updated.')
        else:
            messages.success(request, 'User was successfully added.')


class LogEntryAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_filter = ['action_time','user_id']
    change_list_template = 'admin/courses/logentry_change_list.html'

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        ak_tz = timezone.activate(zoneinfo.ZoneInfo('Asia/Kolkata'))
        if not request.GET.get('action_time__gte') and not request.GET.get('action_time__lte'):
            fdate = timezone.localdate(timezone=ak_tz).strftime('%Y-%m-%d 00:00:00')
            tdate = timezone.localdate(timezone=ak_tz).strftime('%Y-%m-%d 23:59:59')
            from_date = datetime.datetime.fromisoformat(fdate)
            to_date = datetime.datetime.fromisoformat(tdate)
            return super().get_queryset(request).filter(action_time__gte=timezone.make_aware(from_date), action_time__lte=timezone.make_aware(to_date))
        elif request.GET.get('action_time__gte') and request.GET.get('action_time__lte'):
            modified_get = request.GET.copy()
            from_date = request.GET.get('action_time__gte').split('+')[0]
            to_date = request.GET.get('action_time__lte').split('+')[0]
            from_date = datetime.datetime.fromisoformat(from_date)
            to_date = datetime.datetime.fromisoformat(to_date)
            modified_get['action_time__gte'] = timezone.make_aware(from_date,timezone=ak_tz)
            modified_get['action_time__lte'] = timezone.make_aware(to_date,timezone=ak_tz)
            request.GET = modified_get
        return super().get_queryset(request)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        superadmin = User.objects.filter(is_superuser=True)
        staff = User.objects.filter(is_staff=True)
        extra_context['users'] = superadmin | staff
        if not request.GET.get('action_time__gte') and not request.GET.get('action_time__lte'):
            extra_context['from_date'] = datetime.datetime.today().strftime('%Y-%m-%d')
            extra_context['to_date'] = datetime.datetime.today().strftime('%Y-%m-%d')
        else:
            extra_context['from_date'] = request.GET.get('action_time__gte').split(' ')[0]
            extra_context['to_date'] = request.GET.get('action_time__lte').split(' ')[0]
        return super().changelist_view(request, extra_context)

class SubscriptionAdmin(admin.ModelAdmin):

    list_per_page = 10

    add_form_template = 'admin/courses/subscription_add_form.html'
    change_list_template = 'admin/courses/subscription_change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<object_id>/edit_subscription/', self.edit_subscription, name='edit_subscription'),
        ]
        return custom_urls + urls

    def edit_subscription(self, request, object_id):
        self.change_form_template = 'admin/courses/subscription_edit_form.html'
        return self.change_view(request, object_id)

    def message_user(self, request: HttpRequest, message: str, level: Union[int, str] = 'info', extra_tags: str = '', fail_silently: bool = False) -> None:
        if level == messages.SUCCESS:
            pass
        elif level == messages.WARNING or level == messages.ERROR:
            extra_tags = ''
            return super().message_user(request, message, level, extra_tags, fail_silently)
        
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            messages.success(request, 'Subscription was successfully updated.')
        else:
            messages.success(request, 'Subscription was successfully added.')
    
    def delete_model(self, request, obj):
        super().delete_model(request,obj)
        messages.success(request, 'Subscription was successfully deleted.')

    def add_view(self, request, form_url='', extra_context=None):
        courses = CourseModel.objects.filter(status=True, flag__contains=['Upselling'])
        user_model_query = User.objects.annotate(pcourse_count=Count('purchasedcourse'))
        users = user_model_query.filter(is_superuser=False,is_staff=False,pcourse_count__gt=0)
        extra_context = extra_context or {}
        extra_context['courses'] = courses
        extra_context['users'] = users
        response = super().add_view(request, form_url, extra_context)
        return response
    
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        courses = CourseModel.objects.filter(status=True, flag__contains=['Upselling'])
        user_model_query = User.objects.annotate(pcourse_count=Count('purchasedcourse'))
        users = user_model_query.filter(is_superuser=False,is_staff=False,pcourse_count__gt=0)
        extra_context = extra_context or {}
        extra_context['courses'] = courses
        extra_context['users'] = users
        return super().changeform_view(request, object_id, form_url, extra_context)

medics_admin_site = MedicsAdminSite(name="medics_admin")
# Register your models here.
medics_admin_site.register(Group, GroupAdmin)
medics_admin_site.register(User, CustomUserAdmin)
medics_admin_site.register(CourseModel, CourseModelAdmin)
medics_admin_site.register(ModuleModel, ModuleModelAdmin)
medics_admin_site.register(ModulesMediaFile, ModulesMediaFileAdmin)
medics_admin_site.register(Question, QuestionAdmin)
medics_admin_site.register(Choice)
medics_admin_site.register(PopupQuestion, PopupQuestionAdmin)
medics_admin_site.register(PopupChoice)
medics_admin_site.register(LogEntry, LogEntryAdmin)
medics_admin_site.register(Subscription, SubscriptionAdmin,)
