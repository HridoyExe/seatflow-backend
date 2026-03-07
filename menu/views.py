from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from django.db.models import Count, Avg
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Category, MenuItem, Review,MenuImage
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    ReviewSerializer,
    MenuImageSerializer,
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .filters import MenuItemFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator
@method_decorator(name='list', decorator=swagger_auto_schema(operation_description="List all images for a specific menu item"))
@method_decorator(name='create', decorator=swagger_auto_schema(operation_description="Upload a new image for a menu item (Admin only)"))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(operation_description="Get details of a specific menu image"))
@method_decorator(name='update', decorator=swagger_auto_schema(operation_description="Update a menu image (Admin only)"))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(operation_description="Partially update a menu image (Admin only)"))
@method_decorator(name='destroy', decorator=swagger_auto_schema(operation_description="Delete a menu image (Admin only)"))
class MenuImageViewSet(ModelViewSet):
    queryset = MenuImage.objects.all()
    serializer_class = MenuImageSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return MenuImage.objects.filter(menu_id=self.kwargs.get("item_pk"))

    def perform_create(self, serializer):
        item_id = self.kwargs.get("item_pk")
        menu_item = MenuItem.objects.get(id=item_id)

        serializer.save(menu=menu_item)
    
@method_decorator(name='list', decorator=swagger_auto_schema(operation_description="List all menu categories with their item counts"))
@method_decorator(name='create', decorator=swagger_auto_schema(operation_description="Create a new menu category (Admin only)"))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(operation_description="Get details of a specific category"))
@method_decorator(name='update', decorator=swagger_auto_schema(operation_description="Update a category (Admin only)"))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(operation_description="Partially update a category (Admin only)"))
@method_decorator(name='destroy', decorator=swagger_auto_schema(operation_description="Delete a category (Admin only)"))
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

@method_decorator(name='list', decorator=swagger_auto_schema(operation_description="List all menu items with filtering, searching, and ordering options"))
@method_decorator(name='create', decorator=swagger_auto_schema(operation_description="Create a new menu item (Admin only)"))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(operation_description="Get details of a specific menu item, including its reviews and average rating"))
@method_decorator(name='update', decorator=swagger_auto_schema(operation_description="Update a menu item (Admin only)"))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(operation_description="Partially update a menu item (Admin only)"))
@method_decorator(name='destroy', decorator=swagger_auto_schema(operation_description="Delete a menu item (Admin only)"))
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

@method_decorator(name='list', decorator=swagger_auto_schema(operation_description="List all reviews"))
@method_decorator(name='create', decorator=swagger_auto_schema(operation_description="Create a new review for a menu item"))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(operation_description="Get details of a specific review"))
@method_decorator(name='update', decorator=swagger_auto_schema(operation_description="Update a review (Owner or Admin only)"))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(operation_description="Partially update a review (Owner or Admin only)"))
@method_decorator(name='destroy', decorator=swagger_auto_schema(operation_description="Delete a review (Owner or Admin only)"))
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