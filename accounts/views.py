from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from accounts.forms import RegistrationForm, ProfileForm, UserAuthenticationForm
from accounts.models import Account


# Create your views here.

class RegisterView(CreateView):
    model = Account
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Successfully registered.')
        return response


class ProfileView(LoginRequiredMixin, UpdateView):
    model = Account
    form_class = ProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Successfully updated.')
        return super().form_valid(form)


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    authentication_form = UserAuthenticationForm
    redirect_field_name = 'next'

    def get_success_url(self):
        user = self.request.user
        messages.success(self.request, f'Welcome Back {user.name}!')
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('accounts:profile')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')