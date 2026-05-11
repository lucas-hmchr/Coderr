from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from profiles_app.models import UserProfile

from .permissions import IsProfileOwnerOrReadOnly
from .serializers import ProfileSerializer


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """Detail view for the user profile."""
    queryset = UserProfile.objects.select_related("user")
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]


class BusinessProfileListView(generics.ListAPIView):
    """List of all business profiles."""
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filters profiles by type BUSINESS."""
        return UserProfile.objects.select_related("user").filter(
            type=UserProfile.BUSINESS,
        )


class CustomerProfileListView(generics.ListAPIView):
    """List of all customer profiles."""
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filters profiles by type CUSTOMER."""
        return UserProfile.objects.select_related("user").filter(
            type=UserProfile.CUSTOMER,
        )