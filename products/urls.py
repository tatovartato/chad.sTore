from django.urls import path
from products.views import products_view, reviews_view, product_view

urlpatterns = [
    path('products/', products_view, name="products"),
    path('products/<int:pk>', product_view, name='product'),
    path('reviews/', reviews_view, name="reviews")
]