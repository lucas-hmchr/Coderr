from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound

from orders_app.models import Order
from profiles_app.models import UserProfile

from .permissions import IsCustomerUser, IsOrderBusinessUser
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
)


class OrderListCreateView(generics.ListCreateAPIView):
    """View for listing and creating orders."""
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns orders for the current user."""
        user = self.request.user

        return Order.objects.select_related(
            "customer_user",
            "business_user",
        ).filter(
            Q(customer_user=user) | Q(business_user=user),
        )

    def get_serializer_class(self):
        """Selects serializer for creation or display."""
        if self.request.method == "POST":
            return OrderCreateSerializer

        return OrderSerializer

    def get_permissions(self):
        """Sets permissions based on method."""
        permissions = [IsAuthenticated()]

        if self.request.method == "POST":
            permissions.append(IsCustomerUser())

        return permissions

    def create(self, request, *args, **kwargs):
        """Creates a new order."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = serializer.save()
        response_data = OrderSerializer(order).data

        return Response(response_data, status=status.HTTP_201_CREATED)


class OrderUpdateDeleteView(generics.GenericAPIView):
    """View for updating (status) or deleting orders."""
    queryset = Order.objects.select_related("customer_user", "business_user")
    serializer_class = OrderStatusUpdateSerializer

    def get_permissions(self):
        if self.request.method == "PATCH":
            return [IsAuthenticated(), IsOrderBusinessUser()]

        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsAdminUser()]

        return [IsAuthenticated()]

    def patch(self, request, *args, **kwargs):
        """Updates the status of an order."""
        order = self.get_object()
        serializer = self.get_serializer(
            order,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """Deletes an order."""
        order = self.get_object()
        order.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class BusinessOrderCountView(APIView):
    """Base view for counting orders of a business user."""
    permission_classes = [IsAuthenticated]
    status_filter = Order.IN_PROGRESS
    response_key = "order_count"

    def get(self, request, business_user_id):
        """Returns the number of orders."""
        self.validate_business_user(business_user_id)
        count = self.get_order_count(business_user_id)

        return Response({self.response_key: count}, status=status.HTTP_200_OK)

    def validate_business_user(self, business_user_id):
        """Checks if the business user exists."""
        exists = UserProfile.objects.filter(
            user_id=business_user_id,
            type=UserProfile.BUSINESS,
        ).exists()

        if not exists:
            raise NotFound("Business user not found.")

    def get_order_count(self, business_user_id):
        """Calculates the number of orders by status."""
        return Order.objects.filter(
            business_user_id=business_user_id,
            status=self.status_filter,
        ).count()


class CompletedOrderCountView(BusinessOrderCountView):
    """Specialized view for completed orders."""
    status_filter = Order.COMPLETED
    response_key = "completed_order_count"