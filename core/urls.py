# core/urls
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  UserViewSet, UserRegistrationView, UserLoginView, UserProfileView, api_root
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Create a router for the API
router = DefaultRouter() 
router.register('users', UserViewSet)  # Register the User viewset

# URL patterns
urlpatterns = [
    path('', api_root, name='api-root'),  # API root view

    # JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # User endpoints for registration, login, and profile
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('signin/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Router URLs
    path('', include(router.urls)),
     
]
