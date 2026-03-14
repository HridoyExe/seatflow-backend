from djoser.serializers import UserCreateSerializer as BaseUserSerializer
class UserCreateSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ["id","email","password","first_name","last_name","phone","profile_image"]

    def to_internal_value(self, data):
        # Handle 'phonenumber' from frontend by mapping it to 'phone'
        if 'phonenumber' in data and 'phone' not in data:
            data['phone'] = data['phonenumber']
        return super().to_internal_value(data)


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        ref_name= 'CustomUser'
        fields = ["id","email","password","first_name","last_name","phone","profile_image"]
