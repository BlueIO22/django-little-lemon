from rest_framework import serializers
from .models import Booking, Cart, Category, MenuItem, Order, OrderItem

class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    class Meta: 
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'image', 'description']
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta: 
        model = Category
        fields = ['id', 'title', 'slug']
        
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order','menuitem','quantity','unit_price','price']
        
class OrderSerializer(serializers.ModelSerializer):
    delivery_crew = serializers.StringRelatedField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)  
    orderItems = serializers.SerializerMethodField()
    class Meta: 
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'orderItems']
        
    def get_orderItems(self, obj): 
        order = Order.objects.get(pk=obj.id)
        orderItems = OrderItem.objects.filter(order=order)
        return OrderItemSerializer(orderItems, many=True).data
    
class BookingSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Booking
        fields = "__all__"

class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    menuitem = serializers.StringRelatedField()
    class Meta: 
        model = Cart
        fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price', 'price']        
        