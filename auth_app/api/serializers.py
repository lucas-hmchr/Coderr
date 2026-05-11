from django.contrib.auth.models import User
from rest_framework import serializers

from profiles_app.models import UserProfile


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(
        choices=UserProfile.USER_TYPE_CHOICES,
        write_only=True,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "repeated_password",
            "type",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, attrs):
        """Validates that passwords match."""
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """Creates a new user and corresponding profile."""
        user_type = validated_data.pop("type")
        validated_data.pop("repeated_password")

        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, type=user_type)

        return user