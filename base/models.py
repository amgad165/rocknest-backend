from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    made_in = models.CharField(max_length=255, null=True, blank=True)
    material = models.CharField(max_length=255, null=True, blank=True)
    estimated_time = models.CharField(max_length=255, null=True, blank=True)
    custom_size = models.CharField(max_length=255, null=True, blank=True)
    dimension = models.CharField(max_length=255, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    category = models.CharField(max_length=255,default='classic',null=True, blank=True)
    main_image = models.FileField(upload_to='rocknest_images/') 
    
    def __str__(self):
        return self.name
    
class Material(models.Model):
    material_category  = models.CharField(max_length=255)
    finish  = models.CharField(max_length=255)
    available_in = models.CharField(max_length=255)
    material_product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='material_model')


    def __str__(self):
        return self.material_product.name    
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.FileField(upload_to='rocknest_images/')

    def __str__(self):
        return str(self.product) + ' - ' +str(self.image).split('/')[1]
    

class OrderItem(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    def get_total_item_price(self):
        return self.quantity * self.product.price

class Order(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)

    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    '''

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item_price()

        return total
    

class Address(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    post_code = models.CharField(max_length=100)
    state_region = models.CharField(max_length=100)
    
    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username




