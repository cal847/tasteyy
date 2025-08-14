from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "created_at"]

    def create(self, validated_data):
        """Save user to database and hash password"""
        user = User(username=validated_data["username"], email=validated_data["email"])

        # hash password
        user.set_password(validated_data["password"])
        user.save()
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom serializer to login using email"""

    username_field = "email"

    def validate(self, attrs):
        user = self.user
        data = super().validate(attrs)
        data["user"] = {"id": user.id, "username": user.username, "email": user.email}
        return data
