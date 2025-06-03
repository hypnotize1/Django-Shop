from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm

from .models import Account

class RegistrationForm(UserCreationForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    picture = forms.ImageField(required=False)

    class Meta:
        model = Account
        fields = [
            'email',
            'name',
            'phone',
            'date_of_birth',
            'picture',
            'password1',
            'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Enter your {field.replace("_", " ")}'
            })
        self.fields['picture'].widget.attrs['class'] = 'form-control-file'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exists():
            raise ValidationError('Email already registered')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if len(phone) < 10:
            raise ValidationError('Phone number must be at least 10 digits')
        return phone


class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model = Account
        fields = [
            'email',
            'name',
            'phone',
            'date_of_birth',
            'picture',
            'is_staff',
            'is_superuser'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_staff'].help_text = 'Access to the admin panel'
        self.fields['is_superuser'].help_text = 'Access to the admin panel without any permission'


class UserChangeForm(BaseUserChangeForm):
    password = ReadOnlyPasswordHashField(
        label="Password",
    )

    class Meta:
        model = Account
        fields = [
            'email',
            'name',
            'phone',
            'date_of_birth',
            'picture',
            'is_active',
            'is_staff',
            'is_superuser'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_of_birth'].widget = forms.DateInput(attrs={'type': 'date'})


class ProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    class Meta:
        model = Account
        fields = [
            'email',
            'name',
            'phone',
            'date_of_birth',
            'picture',
        ]
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['email'].disabled = True


class UserAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
