from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime
# Create your views here.
def cartItems(request):
    if request.user.is_authenticated:
        
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {
            'get_cart_items': 0,
            'get_cart_total': 0,
        }
        cartItems = order['get_cart_items']
    return cartItems

def store(request):
    products = Product.objects.all()
    context={
        'products':products,
        'cartItems':cartItems(request)
    }
    print(cartItems(request))
    return render(request, "store.html",context)

def cart(request):
    if request.user.is_authenticated:
        
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {
            'get_cart_items': 0,
            'get_cart_total': 0,
        }
    products = Product.objects.all()
    context ={
        'items':items,
        'order':order,
        'cartItems':cartItems(request),
    }
    return render(request, "cart.html", context)

def checkout(request):
    if request.user.is_authenticated:
        
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {
            'get_cart_items': 0,
            'get_cart_total': 0,
            'shipping':False,
        }

    context ={
        'items':items,
        'order':order,
        'cartItems':cartItems(request),
    }
    return render(request, "checkout.html", context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('productId:',productId,'action:',action)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer,complete=False)
    orderItem, created = OrderItem.objects.get_or_create(product=product,order=order)

    if action == 'add':
        orderItem.quantity = orderItem.quantity + 1
    if action == 'remove':
        orderItem.quantity = orderItem.quantity - 1
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    
    return JsonResponse('Item was added',safe=False)

def processOrder(request):
    print(request.body)
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        total = int(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
            )
    # else:
    #     customer, order = guestOrder(request, data)
    return JsonResponse('Payment Successful',safe=False)