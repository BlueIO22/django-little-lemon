from datetime import datetime
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.utils.text import slugify
from django.db.models import Q

from LittleLemonAPI.serializers import CategorySerializer, MenuItemSerializer, OrderSerializer
from LittleLemonAPI.utils import NO_ACCESS, calculate_price, calculate_total, isForbidden
from .models import Category, MenuItem, Order, OrderItem, Cart
from django.contrib.auth.models import User, Group
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
import json

FORBIDDEN_RESPONSE = Response({"message", NO_ACCESS}, status=status.HTTP_403_FORBIDDEN)

# Create your views here.
def home(request):
    return HttpResponse("Hello World")

@api_view(['POST', 'GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def categories(request):
    isAdmin = request.user.is_staff
    
    if request.method == "GET":
        categories = Category.objects.all()    
        return Response(CategorySerializer(categories, many=True).data, status=status.HTTP_200_OK)
    
    if isForbidden(request, groups={}):
        return Response({"message", NO_ACCESS}, status = status.HTTP_403_FORBIDDEN)
    
    if request.method == "POST":
        title = request.data.get("title") or ""
        slug = slugify(title)
        
        if title or slug:
                category = Category.objects.create(title = title, slug = slug)
                return Response(dict({"message":"ok", "category": json.dumps(category)}), status=status.HTTP_200_OK) 
        return Response({"message", "You did not provide enough arguments"}, status = status.HTTP_400_BAD_REQUEST) 

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def category(request, pk):
    isAdmin = request.user.is_staff
    category = Category.objects.get(pk=pk)
    
    if request.method == "GET":
        return Response(CategorySerializer(category).data, status=status.HTTP_200_OK)
    
    if isForbidden(request, groups=dict({"Customer": ["PUT"], "Manager": ["POST"]})):
        return FORBIDDEN_RESPONSE
    

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def menu_items(request):
    isAdmin = request.user.is_staff
    
    if isAdmin == False and request.method == "POST":
        return FORBIDDEN_RESPONSE
    
    if request.method == "GET": 
        menuItems = MenuItem.objects.select_related("category").all()
        serialized_menuItems = MenuItemSerializer(menuItems, many=True)
        return Response(serialized_menuItems.data, status=status.HTTP_200_OK)
    
    if request.method == "POST":
        title = request.data.get("title")
        price = request.data.get("price")
        featured = request.data.get("featured") or False
        category_id = request.data.get("category_id") or 1
        
        if title and price and category_id:
            category = Category.objects.get(pk=category_id) 
            menuItem = MenuItem.objects.create(title = title, price = price, featured = featured, category = category)
            return Response(dict({"message": "menu item created", "menuItem": MenuItemSerializer(menuItem).data}))
    
    return Response({"message", "You did not provide correct amount of arguments"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([])
def menu_item(request, pk):
    menuItem = MenuItem.objects.get(pk=pk)
         
    if request.method == "GET":
        return Response(MenuItemSerializer(menuItem).data, status = status.HTTP_200_OK)

    if isForbidden(request, groups={"Manager": ["PUT"], "Delivery Crew": ["PUT"]}):
        return FORBIDDEN_RESPONSE

    if request.method == "PUT":
        featured = request.data.get("featured")
        if featured: 
            menuItem.featured = featured
            menuItem.save()
            return Response(dict({"message": "menu item updated", "menuItem": MenuItemSerializer(menuItem).data}), status = status.HTTP_200_OK)
        return Response({"message", "Please provide featured flag"}, status = status.HTTP_400_BAD_REQUEST)
    
    if request.method == "DELETE":
        print("Deleting")
        menuItem.delete()
        return Response({"message", "menu item deleted"}, status = status.HTTP_200_OK) 
    
     

@api_view()
@permission_classes([IsAdminUser])
def managers(request):
    username = request.data["username"]
    if username: 
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Manager")

        if request.method == "POST":
            managers.user_set.add(user)
        if request.method == "DELETE":
            managers.user_set.remove(user)
            
        return Response({"message", "ok"})
    
    return Response({"message", "error"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delivery_crew(request):

    if isForbidden(request, groups={"Manager": ["POST", "DELETE"]}):
        return FORBIDDEN_RESPONSE
    
    username = request.data.get("username")
    if username: 
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Delivery Crew")

        if request.method == "POST":
            managers.user_set.add(user)
        if request.method == "DELETE":
            managers.user_set.remove(user)
            
        return Response({"message", "ok"})
    
    return Response({"message", "You did not supply username"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response({"groups": json.dumps([{"name": value.name} for value in request.user.groups.all()])})

def isOrderBlockedForUser(request):
    isDeliveryCrew = request.user.groups.filter(name="Delivery Crew").exists()
    isCustomer = request.user.groups.filter(name="Customer").exists()
    
    if isCustomer and order.user is not request.user:
        return FORBIDDEN_RESPONSE
    
    if isDeliveryCrew and order.delivery_crew is not request.user:
        return FORBIDDEN_RESPONSE


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def orders(request):
    currentUser = User.objects.get(pk=request.user.id) 
    isManager = request.user.groups.filter(name="Manager").exists()
    isAdmin = request.user.is_staff
    
    if request.method == "GET":
        orders = []
        
        if isAdmin or isManager:
            orders = Order.objects.select_related("user", "delivery_crew").all()
        else:
            orders = Order.objects.select_related("user", "delivery_crew").filter(Q(user = currentUser) | Q(delivery_crew = currentUser)).all()
        
        return Response(OrderSerializer(orders, many=True).data, status=status.HTTP_200_OK)
    
    if request.method == "POST":
        user = request.user
        orderlines = request.data.get("orderlines")
        total = calculate_total(orderlines)
        date = datetime.today()
        
        # placing order
        order = Order.objects.create(user = user, date = date, total = total, delivery_crew = None)
        
        if order: 
            for orderline in json.loads(orderlines):
                order = order
                menu_item = MenuItem.objects.get(pk = orderline.get("menu_item"))
                quantity = orderline.get("quantity")
                unit_price = orderline.get("unit_price")
                price = calculate_price(unit_price, quantity)
                
                if order and menu_item and quantity and unit_price and price:
                    OrderItem.objects.create(order=order, quantity=quantity, unit_price = unit_price, price = price, menuitem = menu_item)
            
        return Response({"message", "order created"}, status=status.HTTP_200_OK)
    
    
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def order(request, pk):
    order = Order.objects.select_related("user", "delivery_crew").get(pk=pk)
    isManager = request.user.groups.filter(name="Manager").exists()
    isDeliveryCrew = request.user.groups.filter(name="Delivery Crew").exists()

    isOrderBlockedForUser(request)
    
    if request.method == "GET":
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
    
    if isForbidden(request, groups={"Delivery Crew": ['PUT'], "Manager": ['PUT']}):
        return FORBIDDEN_RESPONSE
    
    if request.method == "PUT":
        delivery_crew = request.data.get("delivery_crew")
        orderstatus = request.data.get("status")
        
        if status and isDeliveryCrew:
            order.status = orderstatus
            return Response({"message", "ok"}, status=status.HTTP_200_OK)
        
        if delivery_crew and isManager:
            deliveryUser = User.objects.filter(username=delivery_crew)[0]
            print(deliveryUser)
            if deliveryUser:
                order.delivery_crew = deliveryUser
                return Response({"message", "ok"}, status=status.HTTP_200_OK) 
            
    return Response({"message": "An Error has occoured"}, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def orderItems(request):
    
    