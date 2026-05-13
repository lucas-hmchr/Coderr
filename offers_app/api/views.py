from django.db.models import Min
from rest_framework import filters, generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from offers_app.models import Offer, OfferDetail

from .permissions import IsBusinessUserOrReadOnly, IsOfferOwnerOrReadOnly
from .serializers import (
    OfferDetailRetrieveSerializer,
    OfferListSerializer,
    OfferSerializer,
    OfferRetrieveSerializer
)
from .pagination import OfferPagination


class OfferViewSet(viewsets.ModelViewSet):
    """ViewSet for managing offers."""
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
    pagination_class = OfferPagination

    def get_permissions(self):
        if self.action in ["list"]:
            return [AllowAny()]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """Returns filtered offers."""
        queryset = self.get_base_queryset()
        queryset = self.filter_by_creator(queryset)
        queryset = self.filter_by_min_price(queryset)
        queryset = self.filter_by_delivery_time(queryset)

        return queryset.distinct()

    def get_base_queryset(self):
        """Creates the base queryset with optimized queries."""
        return Offer.objects.select_related("user").prefetch_related(
            "details",
        ).annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )

    def filter_by_creator(self, queryset):
        """Filters offers by creator."""
        creator_id = self.request.query_params.get("creator_id")

        if creator_id:
            return queryset.filter(user_id=creator_id)

        return queryset

    def filter_by_min_price(self, queryset):
        """Filters offers by minimum price."""
        min_price = self.request.query_params.get("min_price")

        if min_price:
            return queryset.filter(min_price__gte=min_price)

        return queryset

    def filter_by_delivery_time(self, queryset):
        """Filters offers by maximum delivery time."""
        max_delivery_time = self.request.query_params.get("max_delivery_time")

        if max_delivery_time:
            return queryset.filter(min_delivery_time__lte=max_delivery_time)

        return queryset

    def get_serializer_class(self):
        """Selects serializer based on action."""
        if self.action in ["list"]:
            return OfferListSerializer

        if self.action == "retrieve":
            return OfferRetrieveSerializer

        return OfferSerializer


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """Detail view for a single offer detail."""
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailRetrieveSerializer
    permission_classes = [IsAuthenticated]