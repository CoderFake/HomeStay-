from rest_framework import serializers
from Homestays.models import Homestays, HomestayImages, Facilities, Rooms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import re
from django.conf import settings
from botocore.exceptions import NoCredentialsError
import boto3
from django.utils import timezone

User = get_user_model()


class HomestaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Homestays
        fields = '__all__'


class HomestayImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = HomestayImages
        fields = ['image_key']


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facilities
        fields = ['name', 'icon_key', 'description']


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rooms
        fields = ['name', 'amount']


class HomestayUpdateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homestays
        fields = ['id', 'name', 'area', 'address', 'price', 'discount',
                  'max_capacity', 'status', 'description', 'map_key']
        read_only_fields = ['id']
        extra_kwargs = {
            'name': {'required': True},
            'area': {'required': True},
            'address': {'required': True},
            'price': {'required': True},
        }

    def validate(self, data):
        if data['discount'] < 0 or data['discount'] > 100:
            raise serializers.ValidationError('Discount must be between 0 and 100 %')
        if data['price'] < 1000:
            raise serializers.ValidationError('Price must be greater than 1000 VND')
        if data['max_capacity'] < 1:
            raise serializers.ValidationError('Max capacity must be greater than 1')
        if data['area'] < 1:
            raise serializers.ValidationError('Area must be greater than 1')
        return data

    def create(self, validated_data):
        homestay = Homestays.objects.create(**validated_data)
        return homestay

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete_homestay(self, instance):
        instance.is_deleted = True
        instance.save()
        return instance
