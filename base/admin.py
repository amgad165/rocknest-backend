from django.contrib import admin

# Register your models here.
from .models import Product , Order , OrderItem , ProductImage, Address, Material

admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(ProductImage)
admin.site.register(Address)
admin.site.register(Material)
