from django.template.defaultfilters import register


@register.filter
def retailer_price(menuitem, arg):
    return menuitem.retailer_price(arg)
