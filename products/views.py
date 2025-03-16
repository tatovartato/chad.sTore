from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.throttling import UserRateThrottle
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework.exceptions import PermissionDenied

from products.models import Product, Review, FavoriteProduct, Cart, ProductTag, ProductImage, CartItem
from products.serializers import (ProductSerializer, 
                                  ReviewSerializer,
                                  FavoriteProductSerializer,
                                  CartSerializer, 
                                  ProductTagSerializer, 
                                  ProductImageSerializer, 
                                  CartItemSerializer)
from products.permissions import IsObjectOwnerOrReadOnly
from products.pagination import ProductPagination
from products.filters import ProductFilter

class ProductViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                     mixins.ListModelMixin, GenericViewSet):    
    queryset = Product.objects.all() 
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsObjectOwnerOrReadOnly]
    throttle_classes = [UserRateThrottle]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]

    def get_queryset(self):
        return Product.objects.all() if self.request.user.is_staff else Product.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_products(self, request):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsObjectOwnerOrReadOnly]
    filterset_class = ProductFilter
    lookup_field = 'id'
    
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

class FavoriteProductViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                             mixins.ListModelMixin, GenericViewSet):
    serializer_class = FavoriteProductSerializer
    permission_classes = [IsAuthenticated]
    throttle_scope = 'likes'
    
    def get_queryset(self):
        return FavoriteProduct.objects.filter(user=self.request.user)

class CartViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    queryset = Cart.objects.all() 
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, IsObjectOwnerOrReadOnly]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

class TagViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = ProductTag.objects.all()
    serializer_class = ProductTagSerializer
    permission_classes = [IsAuthenticated]

class ProductImageViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                          mixins.ListModelMixin, GenericViewSet):
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated, IsObjectOwnerOrReadOnly]

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs.get('product_pk', 0))
    
class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated, IsObjectOwnerOrReadOnly]
    
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)
    
    def perform_destroy(self, instance):
        if instance.cart.user != self.request.user:
            raise PermissionDenied("You don't have permission to delete this cart item.")
        instance.delete()
    
    def perform_update(self, serializer):
        if self.get_object().cart.user != self.request.user:
            raise PermissionDenied("You don't have permission to update this cart item.")
        serializer.save()