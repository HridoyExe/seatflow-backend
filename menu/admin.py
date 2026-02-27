from django.contrib import admin
from .models import Category, MenuItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    list_filter = ("created_at",)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "is_special",
        "is_available",
    )

    list_filter = (
        "category",
        "is_special",
        "is_available",
        "is_vegetarian",
        "is_spicy",
        "chef_choice",
    )

    search_fields = ("name",)
    list_editable = ("price", "is_special", "is_available")