from rest_framework import serializers

from reviews_app.models import Review
from profiles_app.models import UserProfile


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at'
        ]

        read_only_fields = [
            "id",
            "reviewer",
            "created_at",
            "updated_at"
        ]


class ReviewCreateSerializer(serializers.ModelSerializer):
    BUSINESS_USER_VALIDATION_ERROR = "You can only create reviews for businesses."
    DUPLICATE_REVIEW_ERROR = "You have already reviewed this business."

    class Meta:
        model = Review
        fields = [
            'business_user',
            'rating',
            'description'
        ]

    def validate_business_user(self, value):
        profile_type = value.profile.type
        if profile_type != UserProfile.BUSINESS:
            raise serializers.ValidationError(self.BUSINESS_USER_VALIDATION_ERROR)
        return value

    def validate(self, attrs):
        business_user = attrs["business_user"]
        reviewer = self.context["request"].user

        if Review.objects.filter(
                business_user=business_user,
                reviewer=reviewer,
        ).exists():
            raise serializers.ValidationError(
                {"detail": self.DUPLICATE_REVIEW_ERROR}
            )

        return attrs


class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "rating",
            "description"
        ]
