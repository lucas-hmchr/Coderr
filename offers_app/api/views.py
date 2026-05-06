from django.db.models import Min
from rest_framework import filters, generics, viewsets
from rest_framework.permissions import IsAuthenticated

from offers_app.models import Offer, OfferDetail

from .permissions import IsBusinessUserOrReadOnly, IsOfferOwnerOrReadOnly
from .serializers import (
    OfferDetailRetrieveSerializer,
    OfferListSerializer,
    OfferSerializer,
)


class OfferViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        IsBusinessUserOrReadOnly,
        IsOfferOwnerOrReadOnly,
    ]
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        "title",
        "description",
    ]
    ordering_fields = [
        "updated_at",
        "min_price",
    ]

    def get_queryset(self):
        queryset = self.get_base_queryset()
        queryset = self.filter_by_creator(queryset)
        queryset = self.filter_by_min_price(queryset)
        queryset = self.filter_by_delivery_time(queryset)

        return queryset.distinct()

    def get_base_queryset(self):
        return Offer.objects.select_related("user").prefetch_related(
            "details",
        ).annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )

    def filter_by_creator(self, queryset):
        creator_id = self.request.query_params.get("creator_id")

        if creator_id:
            return queryset.filter(user_id=creator_id)

        return queryset

    def filter_by_min_price(self, queryset):
        min_price = self.request.query_params.get("min_price")

        if min_price:
            return queryset.filter(min_price__gte=min_price)

        return queryset

    def filter_by_delivery_time(self, queryset):
        max_delivery_time = self.request.query_params.get("max_delivery_time")

        if max_delivery_time:
            return queryset.filter(min_delivery_time__lte=max_delivery_time)

        return queryset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return OfferListSerializer

        return OfferSerializer


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailRetrieveSerializer
    permission_classes = [IsAuthenticated]