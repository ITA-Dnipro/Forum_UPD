from django.urls import include, path, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from .views import (
    CustomTokenObtainPairView,
    UserRegistrationView,
    LogoutView
)


app_name = "authentication"

urlpatterns = [
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path("auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.authtoken")),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),

    # JWT implementation
    path('auth/jwt/create/', CustomTokenObtainPairView.as_view(), name='jwt_create'),
    path('auth/jwt/refresh/', TokenRefreshView.as_view(), name='jwt_refresh'),
    path('auth/jwt/verify/', TokenVerifyView.as_view(), name='jwt_verify'),
]
