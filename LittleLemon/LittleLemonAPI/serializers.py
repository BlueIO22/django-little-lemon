from rest_framework import serializers
from .models import Category, MenuItem, Order, OrderItem

class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    class Meta: 
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta: 
        model = Category
        fields = ['id', 'title', 'slug']
        
class OrderSerializer(serializers.ModelSerializer):
    delivery_crew = serializers.StringRelatedField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    class Meta: 
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']
        
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'order','menuitem','quantity','unit_price','price')