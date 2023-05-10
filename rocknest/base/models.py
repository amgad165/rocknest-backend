from django.db import models

# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    made_in = models.CharField(max_length=255)
    material = models.CharField(max_length=255)
    estimated_time = models.CharField(max_length=255)
    custom_size = models.CharField(max_length=255)
    dimension = models.CharField(max_length=255)
    price = models.IntegerField()
    image = models.ImageField(upload_to='product_images/') # new field
    
    def __str__(self):
        return self.name

