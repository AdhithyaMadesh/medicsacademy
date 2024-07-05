from typing import Any,Dict
from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User, Permission
from .models import ModuleModel, Question, PopupQuestion
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator

class CustomStaffProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username','email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(CustomStaffProfileForm, self).__init__(*args, **kwargs)
        user = kwargs.get('instance')

        if user and user.is_superuser==False and user.is_staff :
            del self.fields['username']

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ModuleModelAdminForm(forms.ModelForm):
    # __name__ = 'ModuleModelAdminForm'
    # uploaded_file = MultipleFileField()
    edit_module_field = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = ModuleModel
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        # num_file_fields = kwargs.pop('num_file_fields', 1)
        super().__init__(*args, **kwargs)
        # print(len(args))
        # print(type(args))
        # for j in args:
        #     for m ,v in j.items():
        #         print(f"key {m} value {v}")
                
                   
                

        

      
     
       
       
        # if 'data' in kwargs and int(kwargs['data']['file_num']):
            # for i in range(int(kwargs['data']['file_num'])):
        if len(args) and 'file_num' in args[0]:
            # for i in range(int(args[0]['file_num'])):
            # print(args[0]['file_num'].split(','))
            for i in args[0]['file_num'].split(','):
               
               
                if i != '':
                    k = int(i)
                    ml = f'mlink_{i}'
                    # print(args[0][f'mlink_{k}'])
                    self.fields[f'forder_{k}'] = forms.CharField(required=True, error_messages={'required':'Please enter the file order'},validators=[RegexValidator(regex="^[0-9]*(\.[0-9]{1,2})?$",message="Please enter only numbers or decimals")])
                    if(args[0].get(ml) != ''):
                        self.fields[f'uploaded_file_{k}'] = forms.FileField(required=False,  error_messages={'required':'Please select the file to upload'})
                    else:
                        self.fields[f'uploaded_file_{k}'] = forms.FileField(required=True,  error_messages={'required':'Please select the file to upload'})
                        self.fields[f'mlink_{k}'] = forms.CharField(required=True, error_messages={'required':'Please enter a  link'}, validators=[RegexValidator(regex="^(http|https):\/\/[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?$", message="Please enter a valid link")])

        if len(args) and 'popup_qt_num' in args[0]:
            for j in args[0]['popup_qt_num'].split(','):
                if j != '':
                    l = int(j)
                    self.fields[f'popup_show_time_{l}'] = forms.CharField(required=False, validators=[RegexValidator(regex="^[0-9]*$",message="Please enter only numbers")])
                    self.fields[f'popup_question_{l}'] = forms.CharField(widget=forms.Textarea,required=True, error_messages={'required':'Please enter popup question'})
                    self.fields[f'answer_{l}'] = forms.CharField(widget=forms.RadioSelect, required=True, error_messages={'required':'Please select an answer'})
                    self.fields[f'choices_{l}'] = forms.CharField(widget=forms.MultipleHiddenInput, required=True, error_messages={'required':'Please add options'})


    # def clean(self) -> dict[str, Any]:
    #     cleaned_data = super().clean()
    #     print(cleaned_data)
    #     # if not cleaned_data['uploaded_file']:
    #     #     if cleaned_data['edit_module_field']=='0':
    #     #         self.add_error('uploaded_file', "Please add the media files")
    #     return cleaned_data

    # def clean_uploaded_file(self):
    #     data = self.cleaned_data['uploaded_file']
    #     if not data:
    #         self.add_error('uploaded_file', "Please add the media files")
    #     return data

class QuestionAdminForm(forms.ModelForm):
    answer = forms.CharField(widget=forms.RadioSelect, required=True)
    choices = forms.CharField(widget=forms.MultipleHiddenInput, required=True, error_messages={'required': 'Please add options'})

    class Meta:
        model = Question
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['question_text'].error_messages = {
            'required': 'Please enter the question',
        }

    def clean(self) -> Any:
        cleaned_data = super().clean()
        if 'choices' in cleaned_data and 'answer' not in cleaned_data:
            self.add_error('answer', "Please select an answer")
        return cleaned_data


class CustomUserAdminForm(UserCreationForm):
    is_active = forms.CharField(required=True, error_messages={'required':'Please select status'})
    email = forms.EmailField(required=True, error_messages={'required':'Please enter the email'})
    # permissions = forms.ModelMultipleChoiceField(
    #     queryset=None, widget=forms.SelectMultiple, required=True, error_messages={'required':'Please select permissions'}
    # )
    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['permissions'].queryset = Permission.objects.filter(content_type__app_label='courses').order_by('id')
        self.fields['is_superuser'] = forms.CharField(widget=forms.HiddenInput, required=True)
        self.fields['is_staff'] = forms.CharField(widget=forms.HiddenInput)
        self.fields['date_joined'] = forms.DateTimeField(widget=forms.HiddenInput)
        self.fields['password1'] = forms.CharField(widget=forms.PasswordInput, validators=[validate_password])
        permissions = Permission.objects.filter(content_type__app_label='courses').order_by('id')
        user_permission = Permission.objects.filter(content_type__model='user').order_by('id')
        permission_queryset = permissions | user_permission
        self.fields['user_permissions'] = forms.ModelMultipleChoiceField(queryset=permission_queryset, widget=forms.SelectMultiple, required=True, error_messages={'required':'Please select permissions'})
        del self.fields['password']
        del self.fields['password2']

    
    def clean(self) -> Any:
        cleaned_data = super().clean()
        return cleaned_data

    
class CustomUserChangeAdminForm(UserChangeForm):
    is_active = forms.CharField(required=True, error_messages={'required':'Please select status'})
    email = forms.EmailField(required=True, error_messages={'required':'Please enter the email'})
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','user_permissions']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'] = forms.CharField(widget=forms.PasswordInput, validators=[validate_password], required=False)
        permissions = Permission.objects.filter(content_type__app_label='courses').order_by('id')
        user_permission = Permission.objects.filter(content_type__model='user').order_by('id')
        permission_queryset = permissions | user_permission
        self.fields['user_permissions'] = forms.ModelMultipleChoiceField(queryset=permission_queryset, widget=forms.SelectMultiple, required=True, error_messages={'required':'Please select permissions'})
        del self.fields['password']
    
    def clean(self) -> Any:
        cleaned_data = super().clean()
        return cleaned_data
    
class ImportQuestionForm(forms.Form):
    csvfile = forms.FileField(required=True, error_messages={'required':'Please select a file'})

class PopupQuestionAdminForm(forms.ModelForm):
    answer = forms.CharField(widget=forms.RadioSelect, required=True)
    choices = forms.CharField(widget=forms.MultipleHiddenInput, required=True, error_messages={'required':'Please add options'})
    class Meta:
        model = PopupQuestion
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['popup_question_text'].error_messages = {
            'required': 'Please enter the question',
        }

    def clean(self) -> Any:
        cleaned_data = super().clean()
        if 'choices' in cleaned_data and 'answer' not in cleaned_data:
            self.add_error('answer', "Please select an answer")
        return cleaned_data