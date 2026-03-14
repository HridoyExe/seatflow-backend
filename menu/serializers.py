from rest_framework import serializers
from .models import Category, MenuItem, Review, MenuImage

class MenuImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    class Meta:
        model = MenuImage
        fields = ['id', 'image']

class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )
    average_rating = serializers.FloatField(read_only=True)
    total_reviews = serializers.IntegerField(read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "category",
            "category_name",
            "name",
            "description",
            "price",
            "is_special",
            "is_vegetarian",
            "is_spicy",
            "chef_choice",
            "is_available",
            "average_rating",
            "total_reviews",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

class CategorySerializer(serializers.ModelSerializer):
    menu_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "menu_count",
        ]
        read_only_fields = ["id", "created_at"]





class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(
        source="user.email",
        read_only=True
    )
    menu_item_name = serializers.CharField(
        source="menu_item.name",
        read_only=True
    )
    rating_text = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "user_email",
            "menu_item",
            "menu_item_name",
            "rating",
            "rating_text",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]

    def get_rating_text(self, obj) -> str:
        rating_map = {
            5: "Excellent",
            4: "Very Good",
            3: "Good",
            2: "Fair",
            1: "Poor",
        }
        return rating_map.get(obj.rating, "Average")

    def validate_comment(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Comment cannot be empty."
            )
        return value

    def validate(self, attrs):
        request = self.context.get("request")

        if request and request.method == "POST":
            user = request.user
            menu_item = attrs.get("menu_item")

            if Review.objects.filter(
                user=user,
                menu_item=menu_item
            ).exists():
                raise serializers.ValidationError(
                    "You already reviewed this item."
                )

        return attrs