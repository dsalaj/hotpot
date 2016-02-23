from django.contrib import admin
from hotpot.models import *


class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'category', 'unit_price')

admin.site.register(Category)
admin.site.register(MenuItem, MenuItemAdmin)


class OrderItemAdmin(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    exclude = ('timestamp','order_number',)
    readonly_fields = ('timestamp','order_number',)
    inlines = [
        OrderItemAdmin,
    ]

admin.site.register(Order, OrderAdmin)
admin.site.register(Coupon)
admin.site.register(Menu)
admin.site.register(Retailer)