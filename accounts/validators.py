from django.core.validators import RegexValidator


phone_validator = RegexValidator(
    regex=r'^09\d{9}$',
    message="Phone number must be entered in the format: '09123456789'. Up to 11 digits allowed."
)

postal_code_validator = RegexValidator(
    regex=r'^\d{10}$',
    message="Postal code must up to 10 digits allowed."
)

# user phone and email validation
