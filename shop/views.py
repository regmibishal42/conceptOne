import json
import requests
from django.views.generic import View
from django.shortcuts import redirect, render
from django.http import HttpResponse, response
from .models import Orders, Product,Contact,orderUpdate
from math import ceil
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm

import xml.etree.ElementTree as Et

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
    if query in item.product_name.lower():
        return True
    elif query in item.desc.lower():
        return True
    elif query in item.categoty.lower():
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
        order = Orders(items_json=items_json,name=name,email=email,amount=amount,address=address,city=city,state=state,phone=phone)
        order.save()
        update = orderUpdate(order_id=order.order_id,update_desc="Your Order Has Been Placed")
        update.save()
        thank = True

        id = order.order_id
        valuesForPayment = {'id':id,'amount':int(amount)}
        print(valuesForPayment)
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
        status = root[0].text.strip()
        if status == "Success":
            return redirect('/')
        else:
            return redirect('/checkout')

def errorPage(request):
    return render(request,'shop/errorPage.html')




# For Authenticating and Creating users using Django Inbuild Auth Method That
#  handles duplicate usernames and passwords

def registerPage(request):
    # form = UserCreationForm()
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()


    context = {'form':form}
    return render(request,'shop/registerUser.html',context)

