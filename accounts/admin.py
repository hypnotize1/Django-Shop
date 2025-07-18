from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Account
from .forms import UserChangeForm, AdminUserCreationForm


# Register your models here.

class AccountAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = AdminUserCreationForm

    list_display = ('email', 'full_name', 'phone', 'date_of_birth', 'is_staff', 'is_superuser')
    list_filter = ('is_superuser',)

    fieldsets = (
        (None, {'fields': ('email', 'is_staff', 'is_superuser', 'password')}),
        ('Personal info', {'fields': ('full_name', 'phone', 'date_of_birth', 'picture')}),
        ('Groups', {'fields': ('groups',)}),
        ('Permissions', {'fields': ('user_permissions',)}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'is_staff', 'is_superuser', 'password1', 'password2')}),
        ('Personal info', {'fields': ('full_name', 'phone', 'date_of_birth', 'picture')}),
        ('Groups', {'fields': ('groups',)}),
        ('Permissions', {'fields': ('user_permissions',)}),
    )

    search_fields = ('email', 'full_name', 'phone')
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(Account, AccountAdmin)
