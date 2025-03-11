from django.urls import include, path, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from .views import (
    CustomTokenObtainPairView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    PasswordChangeView,
    UserRegistrationView,
    LogoutView,
    AccountActivationView,
)

app_name = "authentication"

urlpatterns = [
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/activate/', AccountActivationView.as_view(), name='activate'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path(
        "auth/password-reset/",
        PasswordResetRequestView.as_view(),
        name="password_reset"
    ),
    path(
        "auth/password-reset-confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm"
    ),
    path("auth/password-change/", PasswordChangeView.as_view(), name="password_change"),

    # JWT implementation
    path('auth/jwt/create/', CustomTokenObtainPairView.as_view(), name='jwt_create'),
    path('auth/jwt/refresh/', TokenRefreshView.as_view(), name='jwt_refresh'),
    path('auth/jwt/verify/', TokenVerifyView.as_view(), name='jwt_verify'),
]
