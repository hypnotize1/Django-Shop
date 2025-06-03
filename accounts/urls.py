from django.urls import path

from .views import (RegisterView,
                    ProfileView,
                    CustomLoginView,
                    CustomLogoutView,
                    UserPasswordResetConfirmView,
                    UserPasswordResetDoneView,
                    UserPasswordResetCompleteView,
                    UserPasswordResetView,
                    UserPasswordChangeView,
                    UserPasswordChangeDoneView
                    )


# Create your tests here.

app_name = 'accounts'
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('password_reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', UserPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password-change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', UserPasswordChangeDoneView.as_view(), name='password_change_done'),

]