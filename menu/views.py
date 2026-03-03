from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Avg, Count
from .models import Category, MenuItem, Review
from .serializers import CategorySerializer, MenuItemSerializer, ReviewSerializer
from .filters import MenuItemFilter

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuItemViewSet(ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MenuItemFilter
    search_fields = ["name", "description"]
    ordering_fields = ["price", "average_rating", "created_at"]

    def get_queryset(self):
        return MenuItem.objects.select_related("category").annotate(
            average_rating=Avg("reviews__rating"),
            total_reviews=Count("reviews")
        )

    filterset_fields = [
        "is_special",
        "is_vegetarian",
        "is_spicy",
        "chef_choice",
        "is_available",
        "category",
    ]

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        queryset = Review.objects.select_related("user", "menu_item")

        item_id = self.kwargs.get("item_pk")
        if item_id:
            queryset = queryset.filter(menu_item_id=item_id)

        return queryset

    def perform_create(self, serializer):
        item_id = self.kwargs.get("item_pk")

        if item_id:
            serializer.save(
                user=self.request.user,
                menu_item_id=item_id
            )
        else:
            serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)