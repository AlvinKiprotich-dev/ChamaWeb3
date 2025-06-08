from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    UserUpdateView,
    PasswordChangeView,
    logout_view,
    verify_email,
    resend_verification_email
)

app_name = 'users'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UserUpdateView.as_view(), name='profile-update'),
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),    path('verify-email/', verify_email, name='verify-email'),
    path('resend-verification/', resend_verification_email, name='resend-verification'),
]
