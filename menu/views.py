from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
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
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.utils.decorators import method_decorator
@extend_schema_view(
    list=extend_schema(
        description="List all images for a specific menu item",
        parameters=[OpenApiParameter("item_pk", OpenApiTypes.INT, location=OpenApiParameter.PATH)]
    ),
    create=extend_schema(
        description="Upload a new image for a menu item (Admin only)",
        parameters=[OpenApiParameter("item_pk", OpenApiTypes.INT, location=OpenApiParameter.PATH)]
    ),
    retrieve=extend_schema(
        description="Get details of a specific menu image",
        parameters=[OpenApiParameter("item_pk", OpenApiTypes.INT, location=OpenApiParameter.PATH)]
    ),
    update=extend_schema(
        description="Update a menu image (Admin only)",
        parameters=[OpenApiParameter("item_pk", OpenApiTypes.INT, location=OpenApiParameter.PATH)]
    ),
    partial_update=extend_schema(
        description="Partially update a menu image (Admin only)",
        parameters=[OpenApiParameter("item_pk", OpenApiTypes.INT, location=OpenApiParameter.PATH)]
    ),
    destroy=extend_schema(
        description="Delete a menu image (Admin only)",
        parameters=[OpenApiParameter("item_pk", OpenApiTypes.INT, location=OpenApiParameter.PATH)]
    ),
)
class MenuImageViewSet(ModelViewSet):
    queryset = MenuImage.objects.all()
    serializer_class = MenuImageSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return MenuImage.objects.filter(menu_id=self.kwargs.get("item_pk"))

    def perform_create(self, serializer):
        item_id = self.kwargs.get("item_pk")
        menu_item = get_object_or_404(MenuItem, id=item_id)

        serializer.save(menu=menu_item)
    
@extend_schema_view(
    list=extend_schema(description="List all menu categories with their item counts"),
    create=extend_schema(description="Create a new menu category (Admin only)"),
    retrieve=extend_schema(description="Get details of a specific category"),
    update=extend_schema(description="Update a category (Admin only)"),
    partial_update=extend_schema(description="Partially update a category (Admin only)"),
    destroy=extend_schema(description="Delete a category (Admin only)"),
)
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

@extend_schema_view(
    list=extend_schema(description="List all menu items with filtering, searching, and ordering options"),
    create=extend_schema(description="Create a new menu item (Admin only)"),
    retrieve=extend_schema(description="Get details of a specific menu item, including its reviews and average rating"),
    update=extend_schema(description="Update a menu item (Admin only)"),
    partial_update=extend_schema(description="Partially update a menu item (Admin only)"),
    destroy=extend_schema(description="Delete a menu item (Admin only)"),
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
            .prefetch_related("reviews", "images")
            .annotate(
                average_rating=Coalesce(
                    Avg("reviews__rating"),
                    0.0
                ),
                total_reviews=Count("reviews", distinct=True)
            )
            .order_by("-created_at")
        )

@extend_schema_view(
    list=extend_schema(
        description="List all reviews",
        parameters=[OpenApiParameter("item_pk", OpenApiTypes.INT, location=OpenApiParameter.PATH)]
    ),
    create=extend_schema(
        description="Create a new review for a menu item",
        parameters=[OpenApiParameter("item_pk", OpenApiTypes.INT, location=OpenApiParameter.PATH)]
    ),
    retrieve=extend_schema(
        description="Get details of a specific review",
        parameters=[OpenApiParameter("item_pk", OpenApiTypes.INT, location=OpenApiParameter.PATH)]
    ),
    update=extend_schema(
        description="Update a review (Owner or Admin only)",
        parameters=[OpenApiParameter("item_pk", OpenApiTypes.INT, location=OpenApiParameter.PATH)]
    ),
    partial_update=extend_schema(
        description="Partially update a review (Owner or Admin only)",
        parameters=[OpenApiParameter("item_pk", OpenApiTypes.INT, location=OpenApiParameter.PATH)]
    ),
    destroy=extend_schema(
        description="Delete a review (Owner or Admin only)",
        parameters=[OpenApiParameter("item_pk", OpenApiTypes.INT, location=OpenApiParameter.PATH)]
    ),
)
class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        item_pk = self.kwargs.get("item_pk")
        return (
            Review.objects
            .filter(menu_item_id=item_pk)
            .select_related("user", "menu_item")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        item_pk = self.kwargs.get("item_pk")
        menu_item = get_object_or_404(MenuItem, pk=item_pk)
        
        # Check for duplicate review
        if Review.objects.filter(user=self.request.user, menu_item=menu_item).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("You have already reviewed this item.")
            
        serializer.save(user=self.request.user, menu_item=menu_item)