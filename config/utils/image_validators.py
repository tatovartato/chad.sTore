from django.core.exceptions import ValidationError
from django.apps import apps
from PIL import Image

def validate_image_size(image):
    size = image.size
    limit = 5
    if size > limit*1024*1024:
        raise ValidationError(f"Max file size is {limit}")

def validate_image_resolution(image):
    min_height, min_width = 300, 300
    max_height, max_width = 4000, 4000
    img = Image.open(image)
    img_width, img_height = img.size

    if img_width >= max_width or img_height >= max_height:
        raise ValidationError("max resolution is 40000x40000 pixel")
    if img_width <= min_width or img_height <= min_height:
        raise ValidationError("min resolution is 300x300 pixel")

def validate_category_image_count(category_id):
    CategoryImage = apps.get_model("categories", "CategoryImage")  
    limit = 5  
    img_count = CategoryImage.objects.filter(category_id=category_id).count()
    if img_count >= limit:
        raise ValidationError("Each category can have a maximum of 5 images.")

def validate_image_count(product_id):
    ProductImage = apps.get_model("products", "ProductImage")
    limit = 5
    img_count = ProductImage.objects.filter(product_id=product_id).count()
    if img_count >= limit:
        raise ValidationError("max picture limit is 5")