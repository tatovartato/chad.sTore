from django.urls import path
from products.views import ProductViewSet, ReviewViewSet

urlpatterns = [
    path('products/', ProductViewSet.as_view(), name="products"),
    path('products/<int:pk>', ProductViewSet.as_view(), name='product'),
    path('reviews/', ReviewViewSet.as_view(), name="reviews")
]