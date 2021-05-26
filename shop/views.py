import json
from django.shortcuts import render
from django.http import HttpResponse
from .models import Orders, Product,Contact,orderUpdate
from math import ceil
from django.views.decorators.csrf import csrf_exempt

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
                    response  = json.dumps([updates,order[0].items_json],default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')

        
    return render(request,'shop/tracker.html')



def search(request):
    return render(request,'shop/search.html')

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
        order = Orders(items_json=items_json,name=name,email=email,amount=amount,address=address,city=city,state=state,phone=phone)
        order.save()
        update = orderUpdate(order_id=order.order_id,update_desc="Your Order Has Been Placed")
        update.save()
        thank = True

        id = order.order_id
        return render(request,'shop/esewa.html')
    return render(request,'shop/checkout.html')


# @csrf_exempt
def handlerequest(request):
    # Esewa Payment Integration
    pass