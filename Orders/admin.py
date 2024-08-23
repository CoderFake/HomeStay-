from django.contrib import admin
from .models import Payment, Order, OrderHomestay


class OrderHomestayInline(admin.TabularInline):
    model = OrderHomestay
    readonly_fields = ('payment', 'user', 'homestay', 'homestay_price', 'homestay_discount')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_code', 'name', 'phone_number', 'email', 'order_total', 'status']
    list_filter = ['status']
    search_fields = ['order_number', 'full_name', 'phone', 'email', 'status']
    list_per_page = 20
    inlines = [OrderHomestayInline]


admin.site.register(Payment)

admin.site.register(Order, OrderAdmin)

admin.site.register(OrderHomestay)
