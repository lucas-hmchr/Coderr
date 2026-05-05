from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from profiles_app.models import UserProfile

from .permissions import IsProfileOwnerOrReadOnly
from .serializers import ProfileSerializer


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.select_related("user")
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]


class BusinessProfileListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.select_related("user").filter(
            type=UserProfile.BUSINESS,
        )


class CustomerProfileListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.select_related("user").filter(
            type=UserProfile.CUSTOMER,
        )