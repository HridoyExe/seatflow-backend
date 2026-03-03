from djoser.serializers import UserCreateSerializer as BaseUserSerializer
class UserCreateSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ["id","email","password","first_name","last_name","phone","profile_image"]


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ["id","email","password","first_name","last_name","phone","profile_image"]
