from rest_framework import serializers
from .models import Product , ProductImage , OrderItem ,Order, Address , Material
from django.contrib.auth.models import User
from django.contrib.auth import authenticate



class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    
class UserRegisterationSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize registeration requests and create a new user.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer class to authenticate users with email and password.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Incorrect Credentials')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'email']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'made_in', 'material', 'estimated_time', 'custom_size', 'dimension', 'price', 'category','main_image' ,'images']


class MaterialProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name', 'description', 'category','price', 'main_image', 'images']

class MaterialSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    id = serializers.IntegerField(source='material_product.id')
    name = serializers.CharField(source='material_product.name')
    description = serializers.CharField(source='material_product.description')
    price = serializers.IntegerField(source='material_product.price')

    class Meta:
        model = Material
        fields = ['id', 'name', 'description', 'price', 'finish', 'available_in', 'main_image', 'images']

    def get_main_image(self, material):
        return material.material_product.main_image.url if material.material_product else None

    def get_images(self, material):
        return [image.url for image in material.material_product.images.all()] if material.material_product else []
    
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



class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id','user', 'first_name', 'last_name', 'address', 'country', 'city', 'phone_number', 'post_code', 'state_region')
