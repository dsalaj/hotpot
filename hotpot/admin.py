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
    exclude = ('timestamp', 'order_number', 'order_year')
    readonly_fields = ('timestamp', 'serial_number',)
    inlines = [OrderItemAdmin, ]


class DeliveryDayAdmin(admin.TabularInline):
    model = DeliveryDays
    extra = 0


class ShippingAdmin(SingletonModelAdmin):
    inlines = [DeliveryDayAdmin, ]


class ItemBatchAdmin(admin.TabularInline):
    model = ItemBatch
    extra = 0

class MenuAdmin(admin.ModelAdmin):
    inlines = [ItemBatchAdmin, ]

admin.site.register(Category)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(Retailer)
admin.site.register(Shipping, ShippingAdmin)
