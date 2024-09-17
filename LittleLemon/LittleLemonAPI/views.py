from datetime import datetime
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.utils.text import slugify
from django.db.models import Q

from LittleLemonAPI import serializers
from LittleLemonAPI.forms import BookingForm
from LittleLemonAPI.serializers import BookingSerializer, CartSerializer, CategorySerializer, MenuItemSerializer, OrderItemSerializer, OrderSerializer
from LittleLemonAPI.utils import NO_ACCESS, calculate_price, calculate_total, isForbidden
from .models import Booking, Category, MenuItem, Order, OrderItem, Cart
from django.contrib.auth.models import User, Group
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage
import json

FORBIDDEN_RESPONSE = Response({"message", NO_ACCESS}, status=status.HTTP_403_FORBIDDEN)
BAD_REQUESTS_RESPONSE = Response({"message", "You did not provide enough arugments"}, status = status.HTTP_400_BAD_REQUEST)

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def reservations(request):
    bookings = Booking.objects.all()
    return render(request, 'bookings.html',{"bookings": json.dumps(BookingSerializer(bookings, many=True).data)})

def book(request):
    form = BookingForm()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form':form}
    return render(request, 'book.html', context)

def menu(request):
    menu_data = MenuItem.objects.all()
    main_data = {"menu": menu_data}
    return render(request, 'menu.html', {"menu": main_data})

def display_menu_item(request, pk=None): 
    if pk: 
        menu_item = MenuItem.objects.get(pk=pk) 
    else: 
        menu_item = "" 
    return render(request, 'menu_item.html', {"menu_item": menu_item}) 

@csrf_exempt
def bookings(request):
    if request.method == 'POST':
        data = json.load(request)
        exist = Booking.objects.filter(reservation_date=data['reservation_date']).filter(
            reservation_slot=data['reservation_slot']).exists()
        if exist==False:
            booking = Booking(
                first_name=data['first_name'],
                reservation_date=data['reservation_date'],
                reservation_slot=data['reservation_slot'],
            )
            booking.save()
        else:
            return HttpResponse("{'error':1}", content_type='application/json')
    
    date = request.GET.get('date', datetime.today().date())

    bookings = Booking.objects.all().filter(reservation_date=date)

    return HttpResponse(json.dumps(BookingSerializer(bookings, many=True).data), content_type='application/json')

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
                return Response(dict({"message":"ok", "category": CategorySerializer(category).data}), status=status.HTTP_200_OK) 
        return BAD_REQUESTS_RESPONSE

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def category(request, pk):
    category = Category.objects.get(pk=pk)
    
    if request.method == "GET":
        return Response(CategorySerializer(category).data, status=status.HTTP_200_OK)
    

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def menu_items(request):
    isAdmin = request.user.is_staff
    
    if isAdmin == False and request.method == "POST":
        return FORBIDDEN_RESPONSE
    
    if request.method == "GET": 
        category_name = request.query_params.get("category")
        ordering = request.query_params.get("ordering")
        menuItems = MenuItem.objects.select_related("category").all()
        perpage = request.query_params.get("perpage", default=2)
        page = request.query_params.get("page", default=1)
        
        if category_name: 
            menuItems = menuItems.filter(category__title = category_name)
        
        if ordering: 
            menuItems = menuItems.order_by(ordering)    
            
        paginator = Paginator(menuItems, per_page=perpage)
        
        try:
            menuItems = paginator.page(number=page)
        except: 
            menuItems = []
            
        serialized_menuItems = MenuItemSerializer(menuItems, many=True)
        return Response(serialized_menuItems.data, status=status.HTTP_200_OK)
    
    if request.method == "POST":
        title = request.data.get("title")
        price = request.data.get("price")
        featured = request.data.get("featured") or False
        imageUrl = request.data.get("imageUrl")
        description = request.data.get("description")
        category_id = request.data.get("category_id") or 1
        
        if title and price and category_id:
            category = Category.objects.get(pk=category_id) 
            menuItem = MenuItem.objects.create(title = title, price = price, featured = featured, category = category, image = imageUrl, description = description)
            return Response(dict({"message": "menu item created", "menuItem": MenuItemSerializer(menuItem).data}))
    
    return BAD_REQUESTS_RESPONSE

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
        return BAD_REQUESTS_RESPONSE
    
    if request.method == "DELETE":
        menuItem.delete()
        return Response({"message", "menu item deleted"}, status = status.HTTP_200_OK) 
    
     

@api_view(['POST'])
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
    
    return BAD_REQUESTS_RESPONSE

@api_view(['POST'])
@permission_classes([])
def customer(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")
    
    foundUser = User.objects.filter(username = username)
    
    if foundUser:
        return Response({"message", "user allready exists"}, status=status.HTTP_200_OK)
    
    if username and email and password:
        user = User.objects.create(
            username = username,
            email = email,
            password = password)
        
        customers = Group.objects.get(name="Customer")
        customers.user_set.add(user)
        
        return Response({"message", "User has been added"}, status=status.HTTP_200_OK)

        
    return Response({"message", ""})
 
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
    
    return BAD_REQUESTS_RESPONSE


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response({"groups": json.dumps([{"name": value.name} for value in request.user.groups.all()])})

def isOrderBlockedForUser(request, order):
    isDeliveryCrew = request.user.groups.filter(name="Delivery Crew").exists()
    isCustomer = request.user.groups.filter(name="Customer").exists()
    
    if isCustomer and order.user is not request.user:
        return FORBIDDEN_RESPONSE
    
    if isDeliveryCrew and order.delivery_crew is not request.user:
        return FORBIDDEN_RESPONSE
    
    return False


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
        date = datetime.today()
        
        cartItems = Cart.objects.filter(user = request.user)
        
        total = 0
        for cartItem in cartItems:
            total += cartItem.price
        
        order = Order.objects.create(user = user, date = date, total = total, delivery_crew = None)
        
        if order: 
            for item in cartItems: 
                OrderItem.objects.create(order=order, quantity=item.quantity, unit_price = item.unit_price, price = item.price, menuitem = item.menuitem)

            Cart.objects.filter(user=user).delete()

        return Response({"message", "order created"}, status=status.HTTP_200_OK)
    
    
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def order(request, pk):
    order = Order.objects.select_related("user", "delivery_crew").get(pk=pk)
    isManager = request.user.groups.filter(name="Manager").exists()
    isDeliveryCrew = request.user.groups.filter(name="Delivery Crew").exists()

    isOrderBlockedForUser(request, order)
    
    if request.method == "GET":
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
    
    if isForbidden(request, groups={"Delivery Crew": ['PUT'], "Manager": ['PUT']}):
        return FORBIDDEN_RESPONSE
    
    if request.method == "PUT":
        delivery_crew = request.data.get("delivery_crew")
        delivered = request.data.get("delivered")
        
        if delivered and isDeliveryCrew:
            order.status = delivered
            order.save()
            return Response({"message", "ok"}, status=status.HTTP_200_OK)
        
        if delivery_crew and isManager:
            deliveryUser = User.objects.filter(username=delivery_crew)[0]
            if deliveryUser:
                order.delivery_crew = deliveryUser
                order.save()
                return Response({"message", "ok"}, status=status.HTTP_200_OK) 
            
    return Response({"message": "An Error has occoured"}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def orderItems(request):
    return Response({"orderItems", OrderItemSerializer(orderItems, many=True)}, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cart(request):
    
    if request.method == "GET":
        carts = Cart.objects.filter(user=request.user)
        return Response(CartSerializer(carts, many=True).data, status = status.HTTP_200_OK)    

    if request.method == "POST": 
        user = User.objects.get(pk=request.user.id)
        menu_item_id = request.data.get("menu_item_id")
        quantity = request.data.get("quantity")
        menuitem = MenuItem.objects.filter(pk=menu_item_id)
       
        if menuitem and user and quantity: 
            price = menuitem.price * int(quantity)
            Cart.objects.create(user=user, menuitem=menuitem, price=price, unit_price=menuitem.price, quantity=quantity)
            currentCart = Cart.objects.filter(user=user)
            return Response(dict({"message": "cart added", "cart": CartSerializer(currentCart, many=True).data}), status=status.HTTP_200_OK)
    
    return BAD_REQUESTS_RESPONSE