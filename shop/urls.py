
from django.urls import path
from . import views

urlpatterns = [
 path("",views.index,name='ShopHome'),
 path('about/',views.about,name="AboutUs"),
 path("contact/",views.contact,name="ContactUs"),
 path("tracker/",views.tracker,name="TrackingStatus"),
 path('products/<int:myid>',views.productView,name="viewProduct"),
 path('search/',views.search,name="search"),
 path("checkout",views.checkout,name='Checkout'),
#  path('esewa-request',views.EsewaRequestView,name="esewarequest")
#  path('handlerequest/',views.handlerequest,name='handlerequest'),
 path('esewaverify',views.EsewaVerifyView.as_view(),name='esewaverify'),
 path('errorPage',views.errorPage,name='errorPage'),


]