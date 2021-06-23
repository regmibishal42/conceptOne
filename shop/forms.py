from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Orders


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        # only these fild will appear in the Regsiter Page
        fields = ['username','email','password1','password2']



class OrderForm(ModelForm):
    class Meta:
        model = Orders
        fields = ['orderStatus','paymentMethod','paymentStatus']



