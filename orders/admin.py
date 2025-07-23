from django.contrib import admin
from .models import Order, OrderItem, Coupon

# Register your models here.


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ('product',)
    fields = ('product', 'variant', 'price', 'quantity')
    extra = 0
    

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__email')
    ordering = ('created_at',)
    inlines = (OrderItemInline,)


admin.site.register(Coupon)