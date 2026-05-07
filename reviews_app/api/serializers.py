from rest_framework import serializers

from reviews_app.models import Review

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

        read_only_fields = ["id", "reviewer", "created_at", "updated_at"]

class ReviewCreateSerializer(serializers.ModelSerializer):
    BUSINESS_PROFILE_TYPE = "business"
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
        if profile_type != self.BUSINESS_PROFILE_TYPE:
            raise serializers.ValidationError(self.BUSINESS_USER_VALIDATION_ERROR)
        return value

    def create(self, validated_data):
        business_user = validated_data["business_user"]
        reviewer = self.context["request"].user
        if self.review_exists_for_business_user(business_user, reviewer):
            raise serializers.ValidationError(self.DUPLICATE_REVIEW_ERROR)
        return Review.objects.create(
            business_user=business_user,
            reviewer=reviewer,
            **validated_data,
        )

    def review_exists_for_business_user(self, business_user, reviewer):
        return Review.objects.filter(
            business_user=business_user,
            reviewer=reviewer
        ).exists()

class ReviewUpdateSerializer(ReviewCreateSerializer):
    class Meta:
        fields = [
            "rating",
            "description"
        ]

    def update(self, instance, validated_data):
        validated_data.pop("business_user", None)
        return super().update(instance, validated_data)