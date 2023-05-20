from django.utils import timezone
import hmac
from django.shortcuts import get_object_or_404, render
import requests
import json
import base64
import hashlib
from django.conf import settings
from django.http import JsonResponse
import time
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Order, OrderItem, Product
from .serializers import ProductSerializer
from django.contrib.auth.models import User
from rest_framework import status
from django.contrib.auth import authenticate, login
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Create your views here.




def main(request):
    return render(request,"main.html")


@swagger_auto_schema(
    method='get',
    operation_description='Get list of all products',
    responses={200: openapi.Response('List of products', schema=ProductSerializer(many=True))}
)
@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
    print('hi')
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    operation_description='Get a specific product by ID',
    responses={
        200: openapi.Response('Product details', schema=ProductSerializer()),
        404: 'Product not found'
    }
)

@api_view(['GET'])
def get_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    serializer = ProductSerializer(product)
    
    return JsonResponse(serializer.data)



@swagger_auto_schema(
    method='POST',
    operation_description='Add to cart',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'qty': openapi.Schema(type=openapi.TYPE_INTEGER),

        },
        required=['id'],
    ),
    responses={
        201: openapi.Response(description='item added to cart successfully'),
        400: openapi.Response(description='Bad request'),
    }
)
@api_view(['POST'])
def add_to_cart(request):
    id = request.data.get('id', None)
    qty = request.data.get('qty', None)


    product = get_object_or_404(Product, id=id)


    order_item_qs = OrderItem.objects.filter(
        product=product,
        user=request.user,
        ordered=False
    )


    if order_item_qs.exists():
        order_item = order_item_qs.first()
        if qty:
            order_item.quantity += qty
        else:
            order_item.quantity += 1
        order_item.save()
    else:
        if qty:
            order_item = OrderItem.objects.create(
            product=product,
            user=request.user,
            ordered=False,
            quantity=qty
            )           
        else:
            order_item = OrderItem.objects.create(
                product=product,
                user=request.user,
                ordered=False
            )
        order_item.save()

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if not order.items.filter(product__id=order_item.id).exists():
            order.items.add(order_item)
            return Response({'success': 'order quantity updated successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Invalid request"}, status=HTTP_400_BAD_REQUEST)



    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        return Response({'success': 'added to cart successfully'}, status=status.HTTP_201_CREATED)




@swagger_auto_schema(
    method='POST',
    operation_description='User sign up',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['username', 'email', 'password'],
    ),
    responses={
        201: openapi.Response(description='User created successfully'),
        400: openapi.Response(description='Bad request'),
    }
)
@api_view(['POST'])
def signup(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    # Validate input data
    if not username or not email or not password:
        return Response({'error': 'Please provide all required fields'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if username or email already exists
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    # Create the user
    user = User.objects.create_user(username=username, email=email, password=password)

    # Optionally, you can perform additional actions here, such as sending a confirmation email

    return Response({'success': 'User created successfully'}, status=status.HTTP_201_CREATED)



@swagger_auto_schema(
    method='POST',
    operation_description='User login',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['username', 'password'],
    ),
    responses={
        200: openapi.Response(description='Login successful'),
        400: openapi.Response(description='Bad request'),
        401: openapi.Response(description='Unauthorized'),
    }
)
@api_view(['POST'])
def login_view(request):
    """
    User login API endpoint.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    # Authenticate user
    user = authenticate(request, username=username, password=password)

    if user is not None:
        # User is authenticated, log them in
        login(request, user)
        return Response({'success': 'Login successful'}, status=status.HTTP_200_OK)
    else:
        # User authentication failed
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



def index(request):
    return render(request, 'index.html')


def payment_form(request):
    return render(request, 'payment_form.html')


def create_order(request):
    api_key = settings.REVOLUT_MERCHANT_API_SECRET
    headers = {'Authorization': f'Bearer {api_key}'}
    order_data = {
        'amount': 5000,
        'currency': 'GBP',
        'description': 'Test Order'
    }
    response = requests.post('https://sandbox-merchant.revolut.com/api/1.0/orders', json=order_data, headers=headers)
    if response.ok:
        order = response.json()
        print(order)
        return render(request, 'checkout.html', {'order': order})
    else:
        return render(request, 'order.html', {'message': 'Failed to create order'})
        