from djoser.serializers import UserSerializer
from rest_framework import serializers

class CustomUserSerializer(UserSerializer):
    is_superuser = serializers.BooleanField(source='auth_user.is_superuser', read_only=True)
    is_staff = serializers.BooleanField(source='auth_user.is_staff', read_only=True)

    class Meta(UserSerializer.Meta):
        fields = tuple(UserSerializer.Meta.fields) + ('is_superuser', 'is_staff',)
