"""rocknest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from base import views
from django.conf import settings
from django.conf.urls.static import static

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from drf_yasg.renderers import  OpenAPIRenderer

schema_view = get_schema_view(
    openapi.Info(
        title="Product API",
        default_version='v1',
        description="API documentation for Product App",
        contact=openapi.Contact(email="contact@productapp.local"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.main,name='main'),
    path('order', views.create_order,name='create_order'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
     # path('user-info/', views.get_user_info, name='user-info'),

    path('rocknest/products/', views.product_list, name='product-list'),
    path('rocknest/products/classic/', views.get_classic_products, name='get_classic_products'),
    path('rocknest/products/modern/', views.get_modern_products, name='get_modern_products'),
    path('rocknest/product/<int:product_id>/', views.get_product, name='get_product'),

    path('rocknest/add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('rocknest/cart_list/', views.cart_list, name='cart_list'),
    path('rocknest/update_cart/', views.update_cart, name='update_cart'),
    path('rocknest/delete_cart/', views.delete_cart, name='delete_cart'),

    path('rocknest/address/get_address_details/', views.get_address_details, name='get_address_details'),
    path('rocknest/address/create_or_update_address/', views.create_or_update_address, name='create_or_update_address'),

    path('rocknest/payment/', views.payment, name='payment'),

    path('rocknest/payment_checkout/', views.payment_checkout, name='payment_checkout'),

    path('rocknest/signup/', views.signup, name='signup'),
    path('rocknest/login/', views.login_view, name='login_view'),

    path('rocknest/user/logout/', views.UserLogoutAPIView.as_view(), name='logout-user'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
