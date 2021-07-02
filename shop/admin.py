from django.contrib import admin

# Register your models here.

from .models import Contact, Product,Orders, Sales,orderUpdate

admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Orders)
admin.site.register(orderUpdate)
admin.site.register(Sales)