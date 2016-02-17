from django.contrib import admin
from hotpot.models import *


class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'category', 'unit_price')

admin.site.register(Category)
admin.site.register(MenuItem, MenuItemAdmin)
