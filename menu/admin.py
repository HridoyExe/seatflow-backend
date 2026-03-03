from django.contrib import admin
from .models import Category, MenuItem, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    list_display_links = ("name",)
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
        "created_at",
    )
    list_display_links = ("name",)

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


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "menu_item", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__email", "menu_item__name", "comment")
    readonly_fields = ("created_at",)
