from django.core.validators import RegexValidator

phone_number_validator = RegexValidator(
    regex=r'^\d{10}$',  # Regex for exactly 10 digits
    message='Phone number must be 10 digits long',
    code='invalid_phone_number'
)