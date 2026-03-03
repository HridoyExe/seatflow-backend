from django.urls import path, include
from rest_framework_nested import routers
from .views import CategoryViewSet, MenuItemViewSet, ReviewViewSet

router = routers.DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("items", MenuItemViewSet, basename="menuitem")

items_router = routers.NestedDefaultRouter(router, "items", lookup="item")
items_router.register("reviews", ReviewViewSet, basename="item-reviews")

urlpatterns = [
    path("", include(router.urls)),        
    path("", include(items_router.urls)),  
]