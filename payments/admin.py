from django.contrib import admin

from .models import Discount, Item, Order, Tax


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "currency")
    search_fields = ("name",)
    list_filter = ("currency",)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "stripe_coupon_id", "percent_off")
    search_fields = ("name", "stripe_coupon_id")


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "stripe_tax_rate_id")
    search_fields = ("name", "stripe_tax_rate_id")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "total_amount", "total_amount_with_discount", "currency", "discount", "created_at")
    search_fields = ("title",)
    filter_horizontal = ("items",)
