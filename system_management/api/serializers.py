
from system_management import constants
from system_management.models import  User
from system_management.general_func_classes import BaseFormSerializer

from rest_framework import serializers
from django.contrib.auth import get_user_model
from system_management.models import UserType
from django.contrib.auth.password_validation import validate_password



class SendEmailSerializer(BaseFormSerializer):
    """Serializer for sending email"""
    context_data = serializers.DictField(
        allow_empty=True,
        required=False,
        read_only=False,
        write_only=False,
        error_messages={
            'required': 'The context data field is required.'
        }
    )
    html_tpl_path = serializers.CharField(
        max_length=100,
        required=True,
        read_only=False,
        write_only=False,
        error_messages={
            'required': 'The html_tpl_path field is required.',
            'max_length': 'The html_tpl_path field must be less than 100 characters.'
        }
    )
    subject = serializers.CharField(
        max_length=100,
        required=True,
        read_only=False,
        write_only=False,
        error_messages={
            'required': 'The subject field is required.',
            'max_length': 'The subject field must be less than 100 characters.'
        }
    )




class UserModelSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    user_type__name = serializers.SerializerMethodField()
    last_login = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

    @staticmethod
    def get_user_type__name(obj):
        return obj.user_type.name if obj.user_type else None

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "last_login",
            "date_joined",
            "user_type_id",
            "user_type__name",
        )


class RegisterSerializer(serializers.Serializer):
    """Serializer for user registration"""
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    user_type = serializers.CharField(required=False)  # e.g., ADMIN, EXPORTER, LOGISTICS

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")  # not needed for User

        user_type_name = validated_data.pop("user_type", None)
        if user_type_name:
            try:
                user_type = UserType.objects.get(name=user_type_name.upper())
            except UserType.DoesNotExist:
                raise serializers.ValidationError({"user_type": "Invalid user type"})
        else:
            raise serializers.ValidationError({"user_type": "User type is required"})

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            user_type=user_type,
        )
        return user
