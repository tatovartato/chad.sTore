from django.core.management.base import BaseCommand
from faker import Faker
import random
from django.contrib.auth import get_user_model
from products.models import Product
from products.choices import Currency

faker = Faker()
User = get_user_model()

class Command(BaseCommand):
    help = "Generate random products"

    def handle(self, *args, **kwargs):
        products_to_create = []
        currencies = [Currency.USD, Currency.EURO, Currency.GEL]

        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR("No users found. Please create a user first."))
            return  

        for _ in range(1000):
            product = Product(
                user=user,  
                name=faker.name(),
                description=faker.text(),
                price=round(random.uniform(1, 1000), 2),
                currency=random.choice(currencies),
                quantity=random.randint(1, 100),
            )
            products_to_create.append(product)

        Product.objects.bulk_create(products_to_create, batch_size=100)
        self.stdout.write(self.style.SUCCESS("✅ 1000 created products!"))
