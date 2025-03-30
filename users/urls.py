from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet, RegisterViewSet, PasswordResetRequestViewSet, PasswordResetConfirmSerializerViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('register', RegisterViewSet, basename='user-registration')
router.register('password_reset', PasswordResetRequestViewSet, basename='password_reset')

urlpatterns = [
    path('password_reset_confirm/<uidb64>/<token>/', PasswordResetConfirmSerializerViewSet.as_view({'post':'create'}), name='password_reset_confirm'),
    path('', include(router.urls)),
]
