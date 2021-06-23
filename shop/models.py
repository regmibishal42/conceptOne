from django.db import models
from django.db.models.base import ModelState
from django.utils.timezone import now

# Create your models here.

class Product(models.Model):
    product_id = models.AutoField
    product_name = models.CharField(max_length=50)
    categoty = models.CharField(max_length=50,default="")
    subcategory = models.CharField(max_length=50,default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=300)
    pub_date = models.DateField()
    image = models.ImageField(upload_to='shop/images',default="")

    def __str__(self):
        return self.product_name

class Contact(models.Model):
    contactId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254,default="")
    phone = models.CharField(max_length=15,default="")
    description = models.CharField(max_length=500,default="")

    def __str__(self):
        return self.name
    

class Orders(models.Model):
    orderChoices = (
        ('Order Received','Order Received'),
        ('Order Pending','Order Pending'),
        ('Order Delivered','Order Delivered')
        )
    paymentChoices =(
        ('notPaid','notPaid'),
        ('paidEsewa','paidEsewa'),
        ('paidOnDelivery','paidOnDelivery')
    )
    order_id = models.AutoField(primary_key=True)
    items_json = models.CharField(max_length=5000,default="")
    amount = models.IntegerField(default=0)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    phone = models.CharField(max_length=13)
    orderDate = models.DateField(default=now)
    orderStatus = models.CharField(max_length=50,choices=orderChoices,default='Order Received')
    paymentMethod = models.CharField(max_length=20,choices=paymentChoices,default='notPaid')
    paymentStatus = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class orderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey(Orders,null=True,on_delete=models.SET_NULL)
    update_desc = models.CharField(max_length=1000)
    timestamp = models.DateField(auto_now_add=True)
    

    def __str__(self):
        return self.update_desc[0:7] + "..."
    
    