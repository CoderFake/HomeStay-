from django.contrib import admin
from .models import Cart, CartItem


class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'date_added']
    list_filter = ['date_added']
    search_fields = ['cart_id']

    class Meta:
        model = Cart


admin.site.register(Cart, CartAdmin)


class CartItemAdmin(admin.ModelAdmin):
    list_display = ['homestay', 'cart', 'homestay_price', 'homestay_discount']
    list_filter = ['homestay']
    search_fields = ['homestay']

    class Meta:
        model = CartItem


admin.site.register(CartItem, CartItemAdmin)
