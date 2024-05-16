from djoser.serializers import UserSerializer
from rest_framework import serializers

class CustomUserSerializer(UserSerializer):
    is_superuser = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    groups = serializers.StringRelatedField(many=True, read_only=True)
    user_permissions = serializers.StringRelatedField(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'is_superuser',
            'is_staff',
            'first_name',
            'last_name',
            'date_joined',
            'last_login',
            'groups',
            'user_permissions',
        )
