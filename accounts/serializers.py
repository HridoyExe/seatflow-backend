from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserSerializer

User = get_user_model()

class AccountUserCreateSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ["id", "email", "password", "first_name", "last_name", "phone", "profile_image"]

    def to_internal_value(self, data):
        # We need a mutable copy if it's a QueryDict
        if hasattr(data, 'copy'):
            data = data.copy()
            
        if 'phonenumber' in data and 'phone' not in data:
            data['phone'] = data['phonenumber']
        return super().to_internal_value(data)


class AccountUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "phone", "address", "profile_image", "role", "is_verified", "is_staff", "is_superuser"]
        read_only_fields = ["id", "email", "role", "is_verified", "is_staff", "is_superuser"]

    def to_internal_value(self, data):
    
        if hasattr(data, 'copy'):
            data = data.copy()
            
        if 'phonenumber' in data and 'phone' not in data:
            data['phone'] = data['phonenumber']
        return super().to_internal_value(data)
