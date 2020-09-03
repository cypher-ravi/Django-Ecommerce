from django.contrib import admin
from core.models import Item,OrderItem,Order,Payment,Coupen
# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered']

admin.site.register(Item),
admin.site.register(OrderItem),
admin.site.register(Order, OrderAdmin),
admin.site.register(Payment),
admin.site.register(Coupen),
