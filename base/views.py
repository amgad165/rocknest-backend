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
from .models import Order, OrderItem, Product, Address, Payment, Material
from .serializers import MaterialSerializer, OrderItemSerializer, ProductSerializer , OrderSerializer,  UserSerializer , UserRegisterationSerializer , UserLoginSerializer ,LogoutSerializer, AddressSerializer
from django.contrib.auth.models import User
from rest_framework import status
from django.contrib.auth import authenticate, login
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.permissions import AllowAny 
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Create your views here.



def main(request):
    return render(request,"index.html")


# @swagger_auto_schema(
#     method='get',
#     operation_description='Get user info',
#     responses={200: openapi.Response('User info', schema=UserSerializer)}
# )
# @api_view(['GET'])
# def get_user_info(request):
#     if request.user.is_authenticated:
#         user = request.user
#         # Customize the data you want to return about the user
#         data = {
#             'id': user.id,
#             'username': user.username,
#             'email': user.email,
#         }
#         return Response(data)
#     else:
#         return Response({"message": "user is not authenticated"}, status=HTTP_400_BAD_REQUEST)    
    


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
    operation_description='Get list of all materials',
    responses={200: openapi.Response('List of products', schema=ProductSerializer(many=True))}
)
@api_view(['GET'])
def materials_list(request):
    materials = Material.objects.all()
    serializer = MaterialSerializer(materials, many=True)

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
    operation_description='Get a specific material by ID',
    responses={
        200: openapi.Response('Material details', schema=MaterialSerializer()),
        404: 'Product not found'
    }
)

@api_view(['GET'])
def get_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    serializer = MaterialSerializer(material)
    
    return JsonResponse(serializer.data)




@swagger_auto_schema(
    method='get',
    operation_description='Get list of classic products, category == classic',
    responses={200: openapi.Response('List of products', schema=ProductSerializer(many=True))}
)
@api_view(['GET'])
def get_classic_products(request):
    products = Product.objects.filter(
        category="classic",

    )
    # products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)

    return Response(serializer.data)



@swagger_auto_schema(
    method='get',
    operation_description='Get list of modern products, category == modern',
    responses={200: openapi.Response('List of products', schema=ProductSerializer(many=True))}
)
@api_view(['GET'])
def get_modern_products(request):
    products = Product.objects.filter(
        category="modern",

    )
    # products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)

    return Response(serializer.data)

@swagger_auto_schema(
    method='POST',
    operation_description='Get cart list',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={

            'username': openapi.Schema(type=openapi.TYPE_STRING),

        },
        required=['username'],
    ),
    responses={
        201: openapi.Response(description='cart items retrieved successfully'),
        400: openapi.Response(description='Bad request'),
    }
)

@api_view(['POST'])
def cart_list(request):
    username = request.data.get('username', None)
    current_user = get_object_or_404(User, username=username)
    order = Order.objects.get(user=current_user, ordered=False)
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
            'username': openapi.Schema(type=openapi.TYPE_STRING),

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
    username = request.data.get('username', None)

    current_user = get_object_or_404(User, username=username)

    print(current_user.username)
    product = get_object_or_404(Product, id=id)

    order_item_qs = OrderItem.objects.filter(
        product=product,
        user=current_user,
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
            user=current_user,
            ordered=False,
            quantity=qty
            )           
        else:
            order_item = OrderItem.objects.create(
                product=product,
                user=current_user,
                ordered=False
            )
        order_item.save()

    order_qs = Order.objects.filter(user=current_user, ordered=False)
    
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
            user=current_user, ordered_date=ordered_date)
        order.items.add(order_item)
        return Response({'success': 'added to cart successfully'}, status=status.HTTP_201_CREATED)



@swagger_auto_schema(
    method='POST',
    operation_description='update product quantity in cart',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={

            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'product_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER),

        },
        required=['username'],
    ),
    responses={
        201: openapi.Response(description='product quantity in cart updated successfully'),
        400: openapi.Response(description='Bad request'),
    }
)


@api_view(['POST'])
def update_cart(request):
    username = request.data.get('username')
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity')

    try:
        cart = OrderItem.objects.get(user__username=username,product__id=product_id)
        cart.quantity = quantity
        cart.save()
        serializer = OrderItemSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except OrderItem.DoesNotExist:
        return Response({'error': 'Product not found in the cart'}, status=status.HTTP_404_NOT_FOUND)





@swagger_auto_schema(
    method='POST',
    operation_description='delete product from cart',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'product_id': openapi.Schema(type=openapi.TYPE_INTEGER),

        },
        required=['username'],
    ),
    responses={
        201: openapi.Response(description='product quantity in cart updated successfully'),
        400: openapi.Response(description='Bad request'),
    }
)

@api_view(['POST'])
def delete_cart(request):
    username = request.data.get('username')
    product_id = request.data.get('product_id')

    try:
        cart = OrderItem.objects.get(user__username=username, product_id=product_id)
        cart.delete()
        return Response({'message': 'Product deleted from the cart'},status=status.HTTP_204_NO_CONTENT)
    except OrderItem.DoesNotExist:
        return Response({'error': 'Product not found in the cart'}, status=status.HTTP_404_NOT_FOUND)
    
@swagger_auto_schema(
    method='POST',
    operation_description="get user's addrress",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['username'],
    ),
    responses={
        200: openapi.Response(description='successful'),
        400: openapi.Response(description='Bad request'),
        401: openapi.Response(description='Unauthorized'),
    }
)
@api_view(['POST'])
def get_address_details(request):
    username = request.data.get('username', None)
    try:
        user_address = Address.objects.get(user__username=username)
        serializer = AddressSerializer(user_address)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Address.DoesNotExist:
        return Response({'error': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)



@swagger_auto_schema(
    method='POST',
    operation_description="get user's addrress",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING),
            'address': openapi.Schema(type=openapi.TYPE_STRING),
            'country': openapi.Schema(type=openapi.TYPE_STRING),
            'city': openapi.Schema(type=openapi.TYPE_STRING),
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
            'post_code': openapi.Schema(type=openapi.TYPE_STRING),
            'state_region': openapi.Schema(type=openapi.TYPE_STRING),

        },
        required=['username'],
    ),
    responses={
        200: openapi.Response(description='successful'),
        400: openapi.Response(description='Bad request'),
        401: openapi.Response(description='Unauthorized'),
    }
)
@api_view(['POST'])
def create_or_update_address(request):
    username = request.data.get('username', None)
    user = get_object_or_404(User, username=username)
    address_data = {
        'user': user.id,
        'first_name': request.data.get('first_name'),
        'last_name': request.data.get('last_name'),
        'address': request.data.get('address'),
        'country': request.data.get('country'),
        'city': request.data.get('city'),
        'phone_number': request.data.get('phone_number'),
        'post_code': request.data.get('post_code'),
        'state_region': request.data.get('state_region')
    }

    try:
        address = Address.objects.get(user=user)
        serializer = AddressSerializer(instance=address, data=address_data)
        

    except Address.DoesNotExist:
        serializer = AddressSerializer(data=address_data)

    if serializer.is_valid():
        address = serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    operation_description='payment',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['username'],
    ),
    responses={
        201: openapi.Response(description='payment created successfully'),
        400: openapi.Response(description='Bad request'),
    }
)


@api_view(['POST'])
def payment_checkout(request):

    username = request.data.get('username', None)

    current_user = get_object_or_404(User, username=username)

    order = Order.objects.get(user=current_user, ordered=False)

    shipping_address = Address.objects.get(user=current_user)



    amount = int(order.get_total() * 100)

    try:


        # create the payment
        payment = Payment()
        payment.user = current_user
        payment.amount = order.get_total()
        payment.save()

        # assign the payment to the order

        order_items = order.items.all()
        order_items.update(ordered=True)
        for item in order_items:
            item.save()

        order.ordered = True
        order.payment = payment
        order.shipping_address = shipping_address
        # order.ref_code = create_ref_code()
        order.save()

        return Response({"message":"Payment saved successfully"},status=HTTP_200_OK)


    except Exception as e:
        # send an email to ourselves
        return Response({"message": "A serious error occurred. We have been notifed."}, status=HTTP_400_BAD_REQUEST)

    return Response({"message": "Invalid data received"}, status=HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    operation_description='revolut',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'amount': openapi.Schema(type=openapi.TYPE_NUMBER),

        },
        required=['username'],
    ),
    responses={
        201: openapi.Response(description='revolut api request sent successfully'),
        400: openapi.Response(description='Bad request'),
    }
)

@api_view(['POST'])
def payment(request):
    username = request.data.get('username', None)
    amount = request.data.get('amount', None)

    current_user = get_object_or_404(User, username=username)

    order = Order.objects.get(user=current_user, ordered=False)

    amount = amount * 100

    try:


        api_key = settings.REVOLUT_MERCHANT_API_SECRET
        headers = {'Authorization': f'Bearer {api_key}'}
        payment_data = {
            'amount': amount,
            'currency': 'GBP',
            'description': 'Payment Order'
        }
        response = requests.post('https://sandbox-merchant.revolut.com/api/1.0/orders', json=payment_data, headers=headers)
        if response.ok:
            payment_response = response.json()




        return Response({"payment_response":payment_response},status=HTTP_200_OK)


    except Exception as e:
        # send an email to ourselves
        return Response({"message": "A serious error occurred. We have been notifed."}, status=HTTP_400_BAD_REQUEST)

    return Response({"message": "Invalid data received"}, status=HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# def payment(request):
#     username = request.data.get('username', None)

#     current_user = get_object_or_404(User, username=username)

#     order = Order.objects.get(user=current_user, ordered=False)

#     shipping_address = Address.objects.get(user=current_user)



#     amount = int(order.get_total() * 100)

#     try:

#             # charge the customer because we cannot charge the token more than once
#         # charge = stripe.Charge.create(
#         #     amount=amount,  # cents
#         #     currency="usd",
#         #     customer=userprofile.stripe_customer_id
#         # )
#         api_key = settings.REVOLUT_MERCHANT_API_SECRET
#         headers = {'Authorization': f'Bearer {api_key}'}
#         payment_data = {
#             'amount': amount,
#             'currency': 'GBP',
#             'description': 'Payment Order'
#         }
#         response = requests.post('https://sandbox-merchant.revolut.com/api/1.0/orders', json=payment_data, headers=headers)
#         if response.ok:
#             payment_response = response.json()

#         # create the payment
#         payment = Payment()
#         payment.user = current_user
#         payment.amount = order.get_total()
#         payment.save()

#         # assign the payment to the order

#         order_items = order.items.all()
#         order_items.update(ordered=True)
#         for item in order_items:
#             item.save()

#         order.ordered = True
#         order.payment = payment
#         order.shipping_address = shipping_address
#         # order.ref_code = create_ref_code()
#         order.save()

#         return Response({"payment_response":payment_response},status=HTTP_200_OK)


#     except Exception as e:
#         # send an email to ourselves
#         return Response({"message": "A serious error occurred. We have been notifed."}, status=HTTP_400_BAD_REQUEST)

#     return Response({"message": "Invalid data received"}, status=HTTP_400_BAD_REQUEST)






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
    # login(request, user)
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
        