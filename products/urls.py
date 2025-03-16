from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers  
from products.views import (
    ProductViewSet, ReviewViewSet, FavoriteProductViewSet, 
    CartViewSet, TagViewSet, ProductImageViewSet, CartItemViewSet
)

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('cart', CartViewSet)
router.register('tags', TagViewSet)
router.register('favorite_products', FavoriteProductViewSet, basename='favorite_products')
router.register('cart_items', CartItemViewSet, basename='cart-items')

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', ReviewViewSet, basename='product-reviews')
products_router.register('images', ProductImageViewSet, basename='product-images')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(products_router.urls)),
]