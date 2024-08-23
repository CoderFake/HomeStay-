from django.contrib.auth import authenticate
from rest_framework import serializers


class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user is not None and user.is_active and user.is_staff:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")