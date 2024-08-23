from rest_framework import serializers
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


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    last_login = serializers.DateTimeField(format='%H:%M:%S %d-%m-%Y')

    class Meta:
        model = User
        fields = ('id', 'name', 'last_login', 'email', 'phone_number', 'address', 'status', 'role')


    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_role(self, obj):
        if obj.is_superuser:
            return "Admin"
        elif obj.is_staff:
            return "Staff"
        else:
            return "Customer"

    def get_last_login(self, obj):
        return obj.formatted_last_login()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password", "confirm_password")
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Password does not match")
        return data


    def create(self, validated_data):
        validated_data.pop("confirm_password", None)

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.save()
        return user


class ResendEmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(style={'input_type': 'email'}, required=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
            if user.status == "active":
                raise serializers.ValidationError("Email already activated")
            return data
        except User.DoesNotExist:
            raise serializers.ValidationError("Email not found")


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(style={'input_type': 'email'}, required=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
            if not user.is_active and user.is_blocked:
                raise serializers.ValidationError("Your account have been blocked!")
            return data
        except User.DoesNotExist:
            raise serializers.ValidationError("Email not found")


class ResetPasswordConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'}, required=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(style={'input_type': 'password'}, required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid login credentials.")
        elif user.status != "active":
            raise serializers.ValidationError("Your account has been blocked!")
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    picture = serializers.ImageField(write_only=True, required=False)
    picture_url = serializers.SerializerMethodField(read_only=True)
    role = serializers.ChoiceField(choices=[('Admin', 'Admin'), ('Staff', 'Staff'), ('Customer', 'Customer')], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.s3_client = self.get_client()

    def get_client(self):
        return boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number',
                  'address', 'picture', 'role', 'picture_key', 'picture_url')
        read_only_fields = ('id', 'email', 'picture_key', 'picture_url')

    def validate(self, data):
        phone_number = data.get('phone_number')
        if phone_number:
            if not re.match(r'^\d+$', phone_number):
                raise serializers.ValidationError("Phone number must contain only digits")

            if len(phone_number) not in [10, 11]:
                raise serializers.ValidationError("Phone number must be 10 or 11 digits long.")

            if User.objects.filter(phone_number=phone_number).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("This phone number is already in use by another account.")

        return data

    def get_picture_url(self, obj):
        if obj.picture_key:
            return self.get_file_url(self.s3_client, settings.AWS_STORAGE_BUCKET_NAME, obj.picture_key)
        return None

    def update(self, instance, validated_data):
        role = validated_data.pop('role', None)
        if role:
            if role == 'Admin':
                instance.is_staff = True
                instance.is_superuser = True
                instance.save()
            elif role == 'Staff':
                instance.is_staff = True
                instance.is_superuser = False
                instance.save()
            elif role == 'Customer':
                instance.is_staff = False
                instance.is_superuser = False
                instance.save()
            else:
                raise serializers.ValidationError("Invalid role specified")
        else:
            raise serializers.ValidationError("You can be change your own role")

        picture = validated_data.pop('picture', None)
        if picture:
            if instance.picture_key:
                self.delete_from_s3(instance.picture_key)
            instance.picture_key = self.upload_to_s3(picture, instance.id)
            instance.save()
        instance = super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        representation = super(UserProfileSerializer, self).to_representation(instance)
        picture_url = self.get_file_url(self.s3_client, settings.AWS_STORAGE_BUCKET_NAME, instance.picture_key) if instance.picture_key else None
        representation['picture_url'] = picture_url
        representation['role'] = self.get_role(instance)

        return representation

    def get_role(self, obj):
        if obj.is_superuser:
            return "Admin"
        elif obj.is_staff:
            return "Staff"
        return "Customer"

    def upload_to_s3(self, file, user_id):
        key = f'user_pictures/user_{user_id}/{file.name}'
        self.s3_client.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, key, ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'})
        return key

    def get_file_url(self, s3_client, bucket, object_name):
        try:
            url = f"https://{bucket}.s3.amazonaws.com/{object_name}"
            return url
        except Exception as e:
            return f"Error generating URL: {e}"

    def delete_from_s3(self, key):
        self.s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)


class UserPictureDeleteSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        if instance.picture_key:
            self.context['view'].delete_from_s3(instance.picture_key)
            instance.picture_key = None
            instance.save()
        return instance



