from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]
        read_only_fields = ["id"]


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        return f"/api/offerdetails/{obj.id}/"


class OfferListSerializer(serializers.ModelSerializer):
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        ]

    def get_min_price(self, obj):
        prices = [detail.price for detail in obj.details.all()]
        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        times = [detail.delivery_time_in_days for detail in obj.details.all()]
        return min(times) if times else None

    def get_user_details(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username,
        }


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "title",
            "image",
            "description",
            "details",
        ]
        read_only_fields = ["id"]

    def validate_details(self, value):
        required_types = {"basic", "standard", "premium"}
        given_types = {detail["offer_type"] for detail in value}

        if len(value) != 3:
            raise serializers.ValidationError("Exactly three details are required.")

        if given_types != required_types:
            raise serializers.ValidationError(
                "Details must include basic, standard and premium."
            )

        return value

    def create(self, validated_data):
        details_data = validated_data.pop("details")
        offer = Offer.objects.create(
            user=self.context["request"].user,
            **validated_data,
        )
        self.create_details(offer, details_data)

        return offer

    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)

        offer = super().update(instance, validated_data)

        if details_data is not None:
            self.update_details(offer, details_data)

        return offer

    def create_details(self, offer, details_data):
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)

    def update_details(self, offer, details_data):
        for detail_data in details_data:
            offer_type = detail_data.pop("offer_type")
            detail = offer.details.get(offer_type=offer_type)

            for field, value in detail_data.items():
                setattr(detail, field, value)

            detail.save()


class OfferDetailRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]