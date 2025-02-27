from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers  
from categories.views import CategoryDetailView, CategoryImageViewSet, CategoryViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet)

categories_router = routers.NestedDefaultRouter(router, 'categories', lookup='category')
categories_router.register('detail', CategoryDetailView, basename='category-detail')
categories_router.register('images', CategoryImageViewSet, basename='category-images')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(categories_router.urls)),
]
