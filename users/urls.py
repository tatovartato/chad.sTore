from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet, RegisterViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('register', RegisterViewSet, basename='user-registration')

urlpatterns = [
    path('', include(router.urls)),
]
