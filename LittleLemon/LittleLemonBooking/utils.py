
import json
from rest_framework.response import Response
from rest_framework import status

NO_ACCESS = "You dont have access to this resource"

def isForbidden(request, groups):
    
    print(request.user.is_staff)
    if request.user.is_staff:
        return False
    
    for groupModel in request.user.groups.all():
        group = groups.get(str(groupModel))

        if group is None:
            return True
        
        if request.method not in group:
            return True
        
    return False

def calculate_total(orderlines):
    sum = 0
    if orderlines:     
        for orderline in json.loads(orderlines):
            unit_price = orderline.get("unit_price")
            quantity = orderline.get("quantity")
            price = calculate_price(unit_price, quantity)
            sum = sum + price
            
    return sum

def calculate_price(unit_price, quantity):
    if unit_price and quantity:
        return unit_price * quantity
    return 0.00