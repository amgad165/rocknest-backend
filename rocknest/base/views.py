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
from .serializers import ProductSerializer , OrderSerializer,  UserSerializer , UserRegisterationSerializer , UserLoginSerializer ,LogoutSerializer
from django.contrib.auth.models import User
from rest_framework import status
from django.contrib.auth import authenticate, login
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.permissions import AllowAny 
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Create your views here.




def main(request):
    return render(request,"main.html")


@swagger_auto_schema(
    method='get',
    operation_description='Get user info',
    responses={200: openapi.Response('User info', schema=UserSerializer)}
)
@api_view(['GET'])
def get_user_info(request):
    if request.user.is_authenticated:
        user = request.user
        # Customize the data you want to return about the user
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
        return Response(data)
    else:
        return Response({"message": "user is not authenticated"}, status=HTTP_400_BAD_REQUEST)    
    


@swagger_auto_schema(
    method='get',
    operation_description='Get list of all products',
    responses={200: openapi.Response('List of products', schema=ProductSerializer(many=True))}
)
@api_view(['GET'])
def product_list(request):
    products = Product.objects.all()
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
    method='get',
    operation_description='Get list of all products in cart',
    responses={200: openapi.Response('List of products in carts', schema=OrderSerializer(many=True))}
)
@api_view(['GET'])
def cart_list(request):
    order = Order.objects.get(user=request.user, ordered=False)
    serializer = OrderSerializer(order)
    return Response(serializer.data)



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
            return Response({'success': 'order updated successfully'}, status=status.HTTP_201_CREATED)
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
    serializer = UserRegisterationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    # Generate tokens
    refresh_token = RefreshToken.for_user(user)
    tokens = {
        'refresh': str(refresh_token),
        'access': str(refresh_token.access_token)
    }

    # Prepare response data
    data = {
        'user': serializer.data,
        'tokens': tokens
    }

    return Response(data, status=status.HTTP_201_CREATED)

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
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data
    login(request, user)
    user_serializer = UserSerializer(user)
    refresh_token = RefreshToken.for_user(user)
    tokens = {
        'refresh': str(refresh_token),
        'access': str(refresh_token.access_token)
    }
    data = {
        'user': user_serializer.data,
        'tokens': tokens
    }
    return Response(data, status=status.HTTP_200_OK)





class UserLogoutAPIView(GenericAPIView):
    """
    An endpoint to logout users.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            refresh_token = serializer.validated_data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

def index(request):
    return render(request, 'checkout.html')


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
        