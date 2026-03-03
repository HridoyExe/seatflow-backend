import django_filters
from .models import MenuItem


class MenuItemFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte"
    )

    max_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte"
    )

    category_name = django_filters.CharFilter(
        field_name="category__name",
        lookup_expr="icontains"
    )

    class Meta:
        model = MenuItem
        fields = [
            "min_price",
            "max_price",
            "category",
            "category_name",
            "is_special",
            "is_vegetarian",
            "is_spicy",
            "is_available",
        ]