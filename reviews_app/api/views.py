from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from reviews_app.models import Review
from reviews_app.api.serializers import (
    ReviewSerializer,
    ReviewCreateSerializer,
    ReviewUpdateSerializer
)
from reviews_app.api.permissions import IsCustomerUser, IsReviewOwner


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for managing reviews."""
    ordering_fields = [
        "rating",
        "updated_at"
    ]

    queryset = Review.objects.select_related("business_user", "reviewer")

    serializer_class = ReviewSerializer

    def get_queryset(self):
        """Returns reviews filtered by business user or reviewer."""
        queryset = Review.objects.select_related("business_user", "reviewer")
        business_user_id = self.request.query_params.get("business_user_id")
        reviewer_id = self.request.query_params.get("reviewer_id")
        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)
        return queryset

    def get_serializer_class(self):
        """Selects serializer based on action (create, update, etc.)."""
        if self.action == "create":
            return ReviewCreateSerializer
        if self.action in ["update", "partial_update"]:
            return ReviewUpdateSerializer
        return ReviewSerializer

    def get_permissions(self):
        """Sets permissions based on action."""
        if self.action == "create":
            return [IsAuthenticated(), IsCustomerUser()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsReviewOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Saves the current user as reviewer."""
        reviewer = self.request.user
        serializer.save(reviewer=reviewer)

    def create(self, request, *args, **kwargs):
        """Creates a new review."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        response_serializer = ReviewSerializer(serializer.instance)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )
