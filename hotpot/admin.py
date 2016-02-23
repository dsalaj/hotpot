from django.contrib import admin
from hotpot.models import *
from solo.admin import SingletonModelAdmin

class MenuItemRetailerPriceAdmin(admin.TabularInline):
    model = MenuItemRetailerPrice
    extra = 0


class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'category', 'unit_price')
    inlines = [MenuItemRetailerPriceAdmin, ]


class OrderItemAdmin(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    exclude = ('timestamp', 'order_number',)
    readonly_fields = ('timestamp', 'order_number',)
    inlines = [OrderItemAdmin, ]

admin.site.register(Category)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Coupon)
admin.site.register(Menu)
admin.site.register(Retailer)
admin.site.register(Shipping, SingletonModelAdmin)
