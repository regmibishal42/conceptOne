from django.db.models import fields
from django.db.models.base import Model
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Contact, Orders, orderUpdate


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        # only these fild will appear in the Regsiter Page
        fields = ['username','email','password1','password2']



class OrderForm(ModelForm):
    class Meta:
        model = Orders
        fields = ['orderStatus','paymentMethod','paymentStatus']


class OrderUpdateForm(ModelForm):
    class Meta:
        model = orderUpdate
        fields = ['update_desc']

class ContactUsForm(ModelForm):
    class Meta:
        model = Contact
        fields = ['name','email','description']



