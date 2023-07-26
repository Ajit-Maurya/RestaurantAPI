from rest_framework import serializers
from . import models

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['id','slug','title']

class MenuItemSerializer(serializers.ModelSerializer):
    category_title = serializers.CharField(source='category.title',read_only=True)
    #above line is used so that rather than showing id of category it shows category title
    class Meta:
        model = models.MenuItem
        fields = ['id','title','price','featured','category','category_title']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = ['user','menuitem','qauntity','unit_price','price']

class OrderSerializers(serializers.ModelSerializer):
    # delivery_person = serializers.CharField(source='delivery_crew.username',read_only=True)
    class Meta:
        model = models.Order
        fields = ['id','user','delivery_crew','status','total','date']

class OrderItemSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.OrderItem
        fields = ['order','menuitem','qauntity','unit_price','price']