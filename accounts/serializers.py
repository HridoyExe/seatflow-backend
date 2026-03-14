from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserSerializer

User = get_user_model()

class AccountUserCreateSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ["id", "email", "password", "first_name", "last_name", "phone", "profile_image"]

    def to_internal_value(self, data):
        # Handle 'phonenumber' from frontend by mapping it to 'phone'
        if 'phonenumber' in data and 'phone' not in data:
            data['phone'] = data['phonenumber']
        return super().to_internal_value(data)


class AccountUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "phone", "address", "profile_image", "role", "is_verified"]
        read_only_fields = ["id", "email", "role", "is_verified"]

    def to_internal_value(self, data):
        # Handle 'phonenumber' from frontend if sent
        if 'phonenumber' in data and 'phone' not in data:
            data['phone'] = data['phonenumber']
        return super().to_internal_value(data)
