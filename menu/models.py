from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="menu_items"
    )

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(
    max_digits=8,
    decimal_places=2,
    validators=[MinValueValidator(Decimal("0.01"))],
    help_text="Price of the item"
)

    image = models.ImageField(
        upload_to="menu_items/",
        null=True,
        blank=True
    )

    is_special = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)
    chef_choice = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


    def __str__(self):
        return self.name


class Review(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ],
        default=5,
        help_text="Rating from 1 to 5 stars"
    )

    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "menu_item")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.menu_item.name} ({self.rating})"