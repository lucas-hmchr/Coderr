from django.contrib.auth.models import User
from rest_framework import serializers

from profiles_app.models import UserProfile


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for viewing and updating user profiles."""
    user = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    email = serializers.EmailField(source="user.email", required=False)

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]
        read_only_fields = ["user", "username", "type", "created_at"]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        if user_data:
            self.update_user(instance.user, user_data)

        return super().update(instance, validated_data)

    def update_user(self, user, user_data):
        for field, value in user_data.items():
            setattr(user, field, value)

        user.save()

class ProfileListSerializer(serializers.ModelSerializer):
    """Serializer for viewing user profiles."""
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        ]
        read_only_field = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        ]
