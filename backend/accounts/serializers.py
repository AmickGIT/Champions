from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import UserProfile


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration with password confirmation."""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2")
        extra_kwargs = {
            "email": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for basic user information."""

    class Meta:
        model = User
        fields = ("id", "username", "email")
        read_only_fields = ("id",)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile with nested user data."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ("user", "balance", "total_points", "is_admin", "created_at")
        read_only_fields = ("balance", "total_points", "is_admin", "created_at")


class LeaderboardUserSerializer(serializers.ModelSerializer):
    """Minimal user serializer for leaderboard display."""

    class Meta:
        model = User
        fields = ("username",)


class LeaderboardSerializer(serializers.ModelSerializer):
    """Serializer for leaderboard entries showing ranking data."""

    user = LeaderboardUserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ("user", "total_points", "balance")
        read_only_fields = ("user", "total_points", "balance")
