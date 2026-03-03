from rest_framework.viewsets import ModelViewSet
from django.db.models import Count, Avg
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Category, MenuItem, Review
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    ReviewSerializer,
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .filters import MenuItemFilter

class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return (
            Category.objects
            .annotate(
                menu_count=Count("menu_items", distinct=True)
            )
            .order_by("name")
        )

class MenuItemViewSet(ModelViewSet):
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = MenuItemFilter
    search_fields = ["name", "description"]
    ordering_fields = ["price", "average_rating", "created_at"]

    def get_queryset(self):
        return (
            MenuItem.objects
            .select_related("category")
            .prefetch_related("reviews")
            .annotate(
                average_rating=Coalesce(
                    Avg("reviews__rating"),
                    0.0
                ),
                total_reviews=Count("reviews", distinct=True)
            )
            .order_by("-created_at")
        )

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        return (
            Review.objects
            .select_related("user", "menu_item")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)