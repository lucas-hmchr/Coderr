from django.urls import path

from .views import (
    BusinessOrderCountView,
    CompletedOrderCountView,
    OrderListCreateView,
    OrderUpdateDeleteView,
)

urlpatterns = [
    path("orders/", OrderListCreateView.as_view(), name="order-list"),
    path("orders/<int:pk>/", OrderUpdateDeleteView.as_view(), name="order-detail"),
    path(
        "order-count/<int:business_user_id>/",
        BusinessOrderCountView.as_view(),
        name="order-count",
    ),
    path(
        "completed-order-count/<int:business_user_id>/",
        CompletedOrderCountView.as_view(),
        name="completed-order-count",
    ),
]