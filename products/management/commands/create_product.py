from django.core.management.base import BaseCommand
from faker import Faker
import random
from products.choices import Currency
faker = Faker()
from products.models import Product

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        products_to_create =[]
        currencies = [
            Currency.USD,
            Currency.EURO,
            Currency.GEL
        ]

        for _ in range(1000):
            name = faker.name()
            description = faker.text()
            price = round(random.uniform(1,1000), 2)
            quantity = random.randint(1,100)
            currency = random.choice(currencies)

            product = Product(
                name = name,
                description = description,
                price = price,
                currency = currency,
                quantity = quantity
            )

            products_to_create.append(product)
        Product.objects.bulk_create(products_to_create, batch_size=100)
        print('created products')