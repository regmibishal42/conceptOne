
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
 path('esewaverify',views.EsewaVerifyView.as_view(),name='esewaverify'),
 path('errorPage/<int:o_id>',views.errorPage,name='errorPage'),
 path('registerPage',views.registerPage,name='registerPage'),
 path('login',views.loginPage,name="login"),
 path('logout',views.logoutUser,name='logout'),
 path('home',views.home,name='home'),
 path('viewProducts',views.viewProducts,name="viewProducts"),
 path('updateOrder/<int:o_id>',views.updateOrder,name='updateOrder'),
 path('deleteOrder/<int:delete_id>',views.deleteOrder,name='deleteOrder'),
 path('viewMessages/<int:c_id>',views.viewContactUs,name='viewMessages'),
 path('deleteContact/<int:c_id>',views.deleteContactMessage,name='deleteContact'),
 path('createProducts',views.createProducts,name='createProducts'),
 path('updateProduct/<int:p_id>',views.updateProducts,name='updateProduct'),
 path('deleteProduct/<int:p_id>',views.deleteProduct,name='deleteProduct'),
 path('sales',views.salesDashboard,name='sales'),



]