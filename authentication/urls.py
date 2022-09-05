from django.urls import path
from . import views

from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'authentication'

urlpatterns = [
    path('signup/', views.SignupAPIView.as_view(), name='signup'),
    path('verify-email/', views.VerifyEmailAPIView.as_view(), name='verify-email'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('request-password-reset-email/', views.RequestPasswordResetEmail.as_view(), name='request-password-reset-email'),
    path('password-reset/<uidb64>/<token>/', views.PasswordResetTokenCheckAPIView.as_view(), name='password-reset-confirm'),
    path('password-reset/', views.PasswordReset.as_view(), name='password-reset')
]
