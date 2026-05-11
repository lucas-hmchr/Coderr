from rest_framework import serializers
from rest_framework.exceptions import NotFound

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for detailed display of an order."""
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating an order from an offer detail."""
    offer_detail_id = serializers.IntegerField()

    def validate_offer_detail_id(self, value):
        try:
            return OfferDetail.objects.select_related("offer__user").get(
                id=value,
            )
        except OfferDetail.DoesNotExist as error:
            raise NotFound("Offer detail not found.") from error

    def create(self, validated_data):
        offer_detail = validated_data["offer_detail_id"]
        request = self.context["request"]

        return Order.objects.create(
            customer_user=request.user,
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
        )


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]

    def validate(self, attrs):
        invalid_fields = set(self.initial_data.keys()) - {"status"}

        if invalid_fields:
            raise serializers.ValidationError(
                "Only the status field can be updated."
            )

        if "status" not in attrs:
            raise serializers.ValidationError(
                {"status": "This field is required."}
            )

        return attrs