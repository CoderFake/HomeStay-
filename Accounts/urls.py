from django.urls import path
from .views import (VerifyTokenEmail, RegisterView, ConfirmResetPassword,
                    LoginView, LogoutView, ResendEmailView, ForgotPasswordView, UserProfileUpdateView)

urlpatterns = [
    path('verify_email/', VerifyTokenEmail.as_view(), name='verify_email'),
    path('reset_password/', ForgotPasswordView.as_view(), name='reset_password'),
    path('confirm_reset_password/', ConfirmResetPassword.as_view(), name='confirm_reset_password'),
    path('api/resend-activation/', ResendEmailView.as_view(), name='resend_activation'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileUpdateView.as_view(), name='profile_update'),
]