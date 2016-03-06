from django.contrib import admin
from hotpot.models import *
from solo.admin import SingletonModelAdmin
from import_export import resources, fields
from import_export.admin import ExportMixin, ExportActionModelAdmin


# EXPORT RESOURCES
class OrderResource(resources.ModelResource):
    items = fields.Field()
    serial_number = fields.Field()
    full_name = fields.Field()
    full_address = fields.Field()
    contact = fields.Field()

    class Meta:
        model = Order
        fields = ('serial_number', 'delivery_date', 'full_name', 'contact',
                  'full_address', 'note', 'total_price', 'items')
        export_order = ('serial_number', 'delivery_date', 'full_name', 'contact',
                        'full_address', 'total_price', 'items')

    def dehydrate_items(self, order):
        return '\n'.join([smart_text(oi) for oi in order.items])

    def dehydrate_serial_number(self, order):
        return smart_text(order.serial_number)

    def dehydrate_full_name(self, order):
        return smart_text(order.title + ' ' + order.first_name + '\n' + order.family_name)

    def dehydrate_full_address(self, order):
        return smart_text(order.address + '\n' + order.zip + ' ' + order.place)

    def dehydrate_contact(self, order):
        return smart_text(order.phone + '\n' + order.email)


class MenuItemRetailerPriceAdmin(admin.TabularInline):
    model = MenuItemRetailerPrice
    extra = 0


class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'category', 'unit_price')
    inlines = [MenuItemRetailerPriceAdmin, ]


class OrderItemAdmin(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(ExportActionModelAdmin):
    resource_class = OrderResource
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

