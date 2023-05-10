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
from .models import Product
from .serializers import ProductSerializer

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
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    operation_description='Get a specific product by ID',
    manual_parameters=[openapi.Parameter('product_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER)],
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
        return render(request, 'main.html', {'message': 'Failed to create order'})
        