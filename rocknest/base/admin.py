from django.contrib import admin

# Register your models here.
from .models import Product , Order , OrderItem , ProductImage

admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(ProductImage)
