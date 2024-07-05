from django import forms
from django.contrib.auth.models import User
from django.core import validators
from .custom_module import phone_number_validator
from django.contrib.auth.forms import PasswordResetForm

class RegistrationForm(forms.Form):

    GENDER = [
        ("F", "Female"),
        ("M", "Male"),
    ]
   
    phone_number = forms.CharField(
        required=True,
        error_messages={'required': 'Phone number is required'},
        validators=[phone_number_validator]
    )

    name = forms.CharField(required = True, error_messages={'required': 'Please enter your name'})
    gender = forms.ChoiceField(required = True, error_messages={'required': 'Please enter your gender'}, choices=GENDER)
    email = forms.EmailField(required = True,validators=[validators.validate_email],error_messages={'required': 'Please enter your email'})
    # country_code = forms.CharField(required = True)

    # def clean(self):
    #     cleaned_data = super().clean()
    #     email = cleaned_data.get('email')
    #     if(User.objects.filter(email=email).exists()):
    #         self.add_error('email', 'Email Already exists!')
    #     return cleaned_data

class RegistrationForm1(forms.Form):
    OCCUPATION = [
        ("S", "Student"),
        ("T", "Teacher"),
        ("O", "Others")
    ]
    occupation = forms.ChoiceField(required=True, error_messages={'required': 'Please enter your occupation'}, choices=OCCUPATION)
    occupation_others = forms.CharField(required=False)
    college = forms.CharField(required=False)
    password = forms.CharField(required=True, error_messages={'required': 'Please enter the password'})
    confirm_password = forms.CharField(required=True, error_messages={'required': 'Please confirm the password'})
    termcheck = forms.BooleanField(required=True)

    def is_valid_password(self, password):
        if len(password) < 8:
            return False

        has_capital = False
        has_number = False
        has_special = False

        for char in password:
            if char.isupper():
                has_capital = True
            elif char.isnumeric():
                has_number = True
            elif char in "!@#$%^&*()_+{}|:\"<>?":
                has_special = True

        return has_capital and has_number and has_special

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.is_valid_password(password):
            raise forms.ValidationError("Password must be at least 8 characters long and contain at least one capital letter, one number, and one special character.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        select_occupation = cleaned_data.get('occupation')
        other_occupation = cleaned_data.get('occupation_others')
        college = cleaned_data.get('college')

        if select_occupation == "S" and college == '':
            self.add_error('college', 'Please enter your college')
        if select_occupation == "O" and other_occupation == '':
            self.add_error('occupation_others', 'Please enter your other occupation')
        if password != confirm_password:
            self.add_error('password', 'Password does not match')

        return cleaned_data

class UserProfileEdit(forms.Form):

    email = forms.EmailField(required = True,validators=[validators.validate_email],error_messages={'required': 'Please enter your email'})
    first_name = forms.CharField(required = True, error_messages={'required': 'Please enter your first name'})
    last_name = forms.CharField(required = True, error_messages={'required': 'Please enter your last name'})
    profile_img = forms.ImageField(required=True, error_messages={'required': 'Please choose your photo'})


class UserProfileChangePassword(forms.Form):

    old_password = forms.CharField(required = True)
    new_password1 = forms.CharField(required = True)
    new_password2 = forms.CharField(required = True)
   
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('new_password1')
        confirm_password = cleaned_data.get('new_password2')

        if(password != confirm_password):
            self.add_error('new_password2', 'Password does not match')
        return cleaned_data



# class CustomPasswordResetForm(PasswordResetForm,RegistrationForm1):
#     email = forms.EmailField(
#         label="Email",
#         max_length=254,
#         widget=forms.EmailInput(attrs={'class': 'form-control'}),
#     )

#     def clean_email(self):
#         email = self.cleaned_data.get('email')
#         if not User.objects.filter(email=email).exists():
#             raise forms.ValidationError("This email address is not associated with any account.")
#         return email

#     def clean_password(self):
#         password = self.cleaned_data.get('password')
#         if not self.is_valid_password(password):
#             raise forms.ValidationError("Password must be at least 8 characters long and contain at least one capital letter, one number, and one special character.")
#         return password