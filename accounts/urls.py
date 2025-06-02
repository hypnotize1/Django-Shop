from django.contrib.auth.views import LoginView
from django.urls import path

from .views import RegisterView, ProfileView, CustomLoginView, CustomLogoutView

# Create your tests here.

app_name = 'accounts'
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

]