from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegistrationViewSet, CustomTokenObtainPairView, LogoutView, CustomTokenRefreshView, UserViewSet
from rest_framework_simplejwt.views import TokenVerifyView

router = DefaultRouter()
router.register('', RegistrationViewSet, basename='register')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='token_logout'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('users/', UserViewSet.as_view({'get': 'list'}), name='user')
]