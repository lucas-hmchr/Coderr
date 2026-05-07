from rest_framework import status
from rest_framework.test import APITestCase

from orders_app.models import Order

from .helpers import OrderTestMixin


class OrderCountTests(OrderTestMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.completed_order = self.create_order(status=Order.COMPLETED)

    def test_authenticated_user_can_get_in_progress_order_count(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.order_count_url(self.business))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_count"], 1)

    def test_authenticated_user_can_get_completed_order_count(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            self.completed_order_count_url(self.business),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["completed_order_count"], 1)

    def test_order_count_returns_404_for_customer_id(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.order_count_url(self.customer))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_completed_count_returns_404_for_unknown_user(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get("/api/completed-order-count/99999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_user_cannot_get_order_count(self):
        response = self.client.get(self.order_count_url(self.business))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_get_completed_order_count(self):
        response = self.client.get(
            self.completed_order_count_url(self.business),
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)