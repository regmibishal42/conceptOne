import json
import datetime
from django.contrib.messages.api import success
from django.db.models.fields import NullBooleanField
from django.db.models.functions.datetime import ExtractMonth
import requests
from django.views.generic import View
from django.shortcuts import redirect, render
from django.http import HttpResponse, response
from .models import Orders, Product,Contact, Sales,orderUpdate
from math import ceil
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.db.models.functions import Extract
from django.db.models import Q
from .forms import CreateUserForm, OrderForm, OrderUpdateForm, ProductUpdateForm

import xml.etree.ElementTree as Et

from django.contrib import messages

# Create your views here.

def index(request):
    products = Product.objects.all()
    allProds = []
    catpods = Product.objects.values('categoty','id')
    cats = {item['categoty'] for item in catpods}
    for cat in cats:
        prod = Product.objects.filter(categoty=cat)
        n = len(prod)
        nslides = n//4 + ceil((n/4)-(n//4))
        allProds.append([prod,range(1,nslides),nslides])
    params = {'allProds':allProds}
    return render(request,'shop/index.html',params)

def searchMatch(query,item):
    # return true only if query matches the items
    # if query in item.desc.lower() or query in item.product_name.lower() or query in item.categoty.lower():
    #     pass
    if query.lower() in item.product_name.lower():
        return True
    elif query.lower() in item.desc.lower():
        return True
    elif query.lower() in item.categoty.lower():
        return True
    else:
        return False


def search(request):
    query = request.GET.get('search')
    allProds = []
    catpods = Product.objects.values('categoty','id')
    cats = {item['categoty'] for item in catpods}
    for cat in cats:
        prodtemp = Product.objects.filter(categoty=cat)
        prod = [item for item in prodtemp if searchMatch(query,item)]

        n = len(prod)
        nslides = n//4 + ceil((n/4)-(n//4))
        if len(prod) != 0:
            allProds.append([prod,range(1,nslides),nslides])
            message = ''
            params = {'allProds':allProds,'message':message}
        if len(allProds) == 0 or len(query)<4:
            message = "Please make sure to enter relevant search query"
            params = {'message':message}
            print('Invalid Request Search')

    
    return render(request,'shop/search.html',params)




def about(request):
    return render(request,'shop/about.html')

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name',"")
        email = request.POST.get("email","")
        phone = request.POST.get("phone","")
        description = request.POST.get('desc',"")
        contact = Contact(name=name,email=email,phone=phone,description=description)
        contact.save()

    return render(request,'shop/contact.html')




def tracker(request):
    if request.method == "POST":
        order_id = request.POST.get('orderId','')
        email = request.POST.get('email','')
        try:
            order = Orders.objects.filter(order_id=order_id,email=email)
            if len(order)>0:
                update = orderUpdate.objects.filter(order_id=order_id)
                updates = []
                for item in update:
                    updates.append({'text':item.update_desc,'time':item.timestamp})
                    response  = json.dumps({"status":"success","updates":updates,"itemJson":order[0].items_json},default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

        
    return render(request,'shop/tracker.html')





def productView(request,myid):
    # fetch the Product using the ID
    product = Product.objects.filter(id=myid)
    similarCatProducts = []
    # finding the same category Products 
    similarProducts = Product.objects.filter(categoty=product[0].categoty)
    # Taking Out the Inetial Product from That category to show in Recommended List
    for similarProduct in similarProducts:
        if similarProduct.id != product[0].id:
            similarCatProducts.append(similarProduct)


    print(similarProducts)
    return render(request,'shop/product.html',{'product':product[0],'similarProducts':similarCatProducts})

def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson',"")
        name = request.POST.get('name','')
        amount  = request.POST.get('amount','')
        email = request.POST.get('email','')
        address = request.POST.get('address','') + ", " + request.POST.get('addressLine2','')
        city = request.POST.get('city','')
        state = request.POST.get('state','')
        phone = request.POST.get('phone','')
        paymentMethod = request.POST.get('paymentMethod','')
        order = Orders(items_json=items_json,name=name,email=email,amount=amount,address=address,city=city,state=state,phone=phone)
        order.save()
        update = orderUpdate(order_id=order.order_id,update_desc="Your Order Has Been Placed" )
        update.save()
        # thank = True

        id = order.order_id
        valuesForPayment = {'id':id,'amount':int(amount)}
        print(valuesForPayment)
        print(paymentMethod)
        if paymentMethod == "Cash On Delivery":
            messages.success(request,'Your Order has Been Placed.You decided for Cash On Delivery Method. Use Your Order Id to track Your Order. Order Id:'+str(id))
            redirect('/checkout')
        else:
            return render(request,'shop/esewa.html',valuesForPayment)
    return render(request,'shop/checkout.html')


# # @csrf_exempt
# def handlerequest(request):
#     # Esewa Payment Integration
#     pass


class EsewaVerifyView(View):
    def get(self,request,*args, **kwargs):
        oid = request.GET.get("oid")
        amount = request.GET.get("amt")
        refid = request.GET.get("refId")
        url ="https://uat.esewa.com.np/epay/transrec"
        d = {
            'amt': amount,
            'scd': 'EPAYTEST',
            'rid': refid,
            'pid':oid,
        }
        resp = requests.post(url, d)
        root = Et.fromstring(resp.content)
        print(root)
        status = root[0].text.strip()
        if status == "Success":
            order = Orders.objects.get(order_id=oid)
            order.paymentMethod = "paidEsewa"
            order.paymentStatus = True
            order.save()
            sale = Sales(order_id=order.order_id,itemsSold = order.items_json,totalPrice = int(float(amount)),customerName = order.name,customerContact = order.phone,soldDate = datetime.date.today())
            sale.save()
            messages.success(request,'Your Order has been received. To Track It use your order Id'+str(oid))
            return redirect('/checkout')

        else:
            messages.warning(request,'Esewa Failure Occured')
            return redirect('/checkout')

def errorPage(request,o_id):
    messages.warning(request,'Due To esewa Failure,we couldnot continue with your payment. Please Pay Via Cash On Delivery. Your Order Id is:'+str(o_id))
    return render(request,'shop/errorPage.html')




# For Authenticating and Creating users using Django Inbuild Auth Method That
#  handles duplicate usernames and passwords


def registerPage(request):
    # form = UserCreationForm()
    if request.user.is_authenticated:
        return redirect('/')
    else:
        form = CreateUserForm()
        if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request,'Account Created for: '+user)
                return redirect('login')


        context = {'form':form}
        return render(request,'shop/registerUser.html',context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method =="POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user  =authenticate(request,username=username,password=password)
            if user is not None:
                login(request,user)
                return redirect('home')
            else:
                messages.info(request,"Username or password is Incorrect")
        context = {}
    return render(request,'shop/login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('/')

@login_required(login_url='login')
def home(request):
    totalOrders = Orders.objects.filter(orderStatus='Order Received').count()
    deliveredOrders = Orders.objects.filter(orderStatus='Order Delivered').count()
    pendingOrders = Orders.objects.filter(orderStatus="Order Pending").count()
    orders = Orders.objects.all()
    contacts = Contact.objects.all()
    context = {'totalOrders':totalOrders,'deliveredOrders':deliveredOrders,'pendingOrders':pendingOrders,'orders':orders,'contacts':contacts}
    return render(request,'admin/dashboard.html',context)

@login_required
def viewProducts(request):
    allProducts = Product.objects.all()
    context = {'products':allProducts}
    return render(request,'admin/viewProducts.html',context)


@login_required
def updateOrder(request,o_id):
    orders = Orders.objects.get(order_id=o_id)
    orderUpdates = orderUpdate.objects.get(order_id=o_id)
    form = OrderForm(instance=orders)
    orderUpdateForm = OrderUpdateForm(instance=orderUpdates)

    if request.method == 'POST':
        form = OrderForm(request.POST,instance=orders)
        orderUpdateForm = OrderUpdateForm(request.POST,instance=orderUpdates)
        if form.is_valid and orderUpdateForm.is_valid:
            form.save()
            orderUpdateForm.save()
            return redirect('/home')


    js = json.loads(orders.items_json)
    orderedItems = dict(js)
    context ={'orders':orders,'orderedItems':orderedItems,'form':form,'updateForm':orderUpdateForm}
    return render(request,'admin/orderUpdate.html',context)



@login_required
def deleteOrder(request,delete_id):
    order = Orders.objects.get(order_id=delete_id)
    orderUpdates = orderUpdate.objects.get(order_id=delete_id)
    print(orderUpdates.order_id)
    if request.method == "POST":
        # if payment has been Paid sent the Order to Sales Model
        if Sales.objects.filter(order_id=delete_id):
            pass
        else:
            print('ID DOES NOT EXIST IN POST')
            sales = Sales(order_id=delete_id,itemsSold = order.items_json,totalPrice=order.amount,customerName=order.name,customerContact=order.phone,soldDate=datetime.date.today())
            sales.save()
        
        order.delete()
        orderUpdates.delete()
        return redirect('home')
    context ={'order':order,'orderUpdates':orderUpdates}
    return render(request,'admin/deleteOrder.html',context)

# @login_required
# def addProducts(request):
#     context={}
#     return render(request,'admin/addProducts.html',context)

@login_required
def viewContactUs(request,c_id):
    contactDetails = Contact.objects.get(contactId=c_id)
    context={'contactDetails':contactDetails}
    return render(request,'admin/contactMessages.html',context)

@login_required
def deleteContactMessage(request,c_id):
    contact = Contact.objects.get(contactId=c_id)
    if request.method == "POST":
        contact.delete()
        return redirect('/home')
    context = {'contact':contact}
    return render(request,'admin/deleteContact.html',context)

@login_required
def createProducts(request):
    
    if request.method == "POST":
        # print(request.POST)
        form = ProductUpdateForm(request.POST,request.FILES)
        if form.is_valid():
            print('Yeha control gayo')
            form.save()
            return redirect('/viewProducts')
        else:
            print(form.errors)
            
    form = ProductUpdateForm()       
    context = {'form':form}
    return render(request,'admin/addProducts.html',context)


@login_required
def updateProducts(request,p_id):
    product = Product.objects.get(id=p_id)
    form = ProductUpdateForm(instance=product)
    if request.method == "POST":
        form = ProductUpdateForm(request.POST,request.FILES,instance=product)
        if form.is_valid:
            form.save()
            return redirect('/viewProducts')
    
    context = {'form':form}
    return render(request,'admin/addProducts.html',context )

@login_required
def deleteProduct(request,p_id):
    product = Product.objects.get(id=p_id)
    if request.method == "POST":
        product.delete()
        return redirect('/viewProducts')
    
    context = {'product':product}
    return render(request,'admin/deleteProduct.html',context)

@login_required
def salesDashboard(request):
    sales = Sales.objects.all()
    # find out Top Sold Items
    SoldProduct = {}
    for sale in sales:
        salesDict = json.loads(sale.itemsSold)
        # print(sale.get_year())
        # print(sale.get_month())
        # print(sale.get_day())
        
        for key,value in salesDict.items():
            if str(value[1]) in SoldProduct.keys():
                SoldProduct[value[1]] += value[0]
                # print('Mouse Exist')
            else:
                SoldProduct[value[1]] = value[0]
    sortedListOfSoldProducts = sorted(SoldProduct.items())
    # since sorted functions converts dict to list 
    # so lets change it to original
    SoldProduct = dict(sortedListOfSoldProducts)
    # print(SoldProduct)

    # Least Sold Products
    

    # Find Total Sales Amount In a Year
    currentDate = datetime.date.today()
    currentweek = int(datetime.date.today().strftime('%V'))
    totalSalesInYear = 0
    salesInYear = Sales.objects.annotate(year=Extract('soldDate','year')).filter(year=currentDate.year)
    # print('Total sales in '+str(currentDate.year)+ "=" +str(salesInYear))
    for sale in salesInYear:
        totalSalesInYear += sale.totalPrice

    # Total Sales In Months
    totalSalesInMonth = 0
    # If this and doesnot work then use q funstion
    #from django.db.models import Q
    # User.objects.filter(Q(income__gte=5000) | Q(income__isnull=True))
    salesInMonth = Sales.objects.annotate(year=Extract('soldDate','year')).filter(year=currentDate.year) and Sales.objects.annotate(month=Extract('soldDate','month')).filter(month = currentDate.month)
    for sale in salesInMonth:
        totalSalesInMonth += sale.totalPrice
    
    # Total Sales in A Week
    totalSalesInWeek = 0
    salesInWeek = Sales.objects.annotate(year=Extract('soldDate','year'),week=Extract('soldDate','week')).filter(Q(year=currentDate.year) and Q(week = currentweek))
    for sale in salesInWeek:
        totalSalesInWeek += sale.totalPrice

    salesByPeriod = {
        'inYear': totalSalesInYear,
        'inMonth' : totalSalesInMonth,
        'inWeek' :totalSalesInWeek
    }
    context ={'sales':sales,'soldProduct':SoldProduct,'salesByPeriod':salesByPeriod}
    return render(request,'admin/sales.html',context)