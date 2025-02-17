from django.urls import path, include
from categories.views import CategoryDetailView, CategoryImageListView, CategoryListView

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name='categories'),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name='catyegory'),
    path("categories/<int:category_id>/images/", CategoryImageListView.as_view(), name='images')
]
