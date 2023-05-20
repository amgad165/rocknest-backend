from rest_framework import serializers
from .models import Product , ProductImage , OrderItem ,Order


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'made_in', 'material', 'estimated_time', 'custom_size', 'dimension', 'price', 'category','main_image' ,'images']



class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    total_item_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            'id',
            'product',
            'quantity',
            'total_item_price'
        )

    def get_product(self, obj):
        return ProductSerializer(obj.product).data

   
    def get_total_item_price(self, obj):
        return obj.get_total_item_price()


class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'order_items',
            'total',
            
        )

    def get_order_items(self, obj):
        return OrderItemSerializer(obj.items.all(), many=True).data

    def get_total(self, obj):
        return obj.get_total()


