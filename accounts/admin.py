from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "email",
        "phone",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "is_verified",
    )

    search_fields = ("email", "phone", "first_name")

    list_filter = ("is_staff", "is_active", "is_verified")

    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),

        ("Personal Info", {
            "fields": ("first_name", "last_name", "phone", "profile_image")
        }),

        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
                "is_verified",
            )
        }),

        ("Important Dates", {
            "fields": ("last_login",)
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "phone", "password1", "password2"),
        }),
    )