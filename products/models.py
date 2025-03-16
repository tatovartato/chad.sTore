from django.db import models
from django.core.validators import MaxValueValidator
from config.model_utils.models import TimeStampedModel
from products.choices import Currency
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.FloatField()
    currency = models.CharField(max_length=255, choices=Currency.choices, default=Currency.GEL)
    tags = models.ManyToManyField("products.ProductTag", related_name='products', blank=True)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

class Review(TimeStampedModel, models.Model):
    product = models.ForeignKey('products.Product', related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', related_name='reviews', on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    rating = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
    
    class Meta:
        unique_together = ['product', 'user']

class FavoriteProduct(TimeStampedModel, models.Model):
    product = models.ForeignKey('products.Product', related_name='favorite_products', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', related_name='favorite_products', on_delete=models.SET_NULL, null=True, blank=True)


class ProductTag(TimeStampedModel, models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.name}"


class Cart(TimeStampedModel, models.Model):
    products = models.ManyToManyField('products.Product', related_name='carts')
    user = models.OneToOneField('users.User', related_name='cart', on_delete=models.SET_NULL, null=True, blank=True)
    

class ProductImage(TimeStampedModel, models.Model):
    image = models.ImageField(upload_to='products/')
    product = models.ForeignKey('products.Product', related_name='images', on_delete=models.CASCADE)
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time_of_addition = models.FloatField()

    def __str__(self):
        return f"{self.product.name} - {self.quantity} items"
    
    def total_price(self):
        return self.quantity * self.price_at_time_of_addition