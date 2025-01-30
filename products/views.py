from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from products.models import Product, Review
from products.serializers import ProductSerializer, ReviewSerializer


@api_view(['GET', 'POST'])
def product_view(request):
    if request.method == 'GET':
        products = Product.objects.all()
        product_list = []
        
        for product in products:
            product_data = {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'currency': product.currency,
            }
            product_list.append(product_data)

        return Response({'products': product_list})
    elif request.method == "POST":
        data = request.data
        serializer = ProductSerializer(data)
        if serializer.is_valid():
            new_product = Product.objects.create(
                name=data.get('name'),
                description=data.get('description'),
                price=data.get('price'),
                currency=data.get('currency', 'GEL')  
            )
            return Response({'id': new_product.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def review_view(request):
    if request.method == 'GET':
        reviews = Review.objects.all()
        review_list = []
        
        for review in reviews:
            review_data = {
                'id': review.id,
                'product_id': review.product.id,
                'content': review.content,
                'rating': review.rating
            }
            review_list.append(review_data)
        
        return Response({'reviews': review_list})

    elif request.method == 'POST':
        serializer = ReviewSerializer(data=request.data, context={"request":request})
        if serializer.is_valid():
            review = serializer.save()
            return Response(
                {'id': review.id, 'message': 'Review created successfully!'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
