from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name_es', 'name_en', 'slug']
    prepopulated_fields = {'slug': ('name_es',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name_es', 'price', 'unit', 'category', 'is_available', 'is_special', 'stock']
    list_filter = ['category', 'is_available', 'is_special']
    list_editable = ['price', 'is_available', 'is_special', 'stock']
    search_fields = ['name_es', 'name_en']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name_es', 'quantity', 'unit', 'price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'created_at']
