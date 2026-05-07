from rest_framework import status
from rest_framework.test import APITestCase

from orders_app.models import Order

from .helpers import OrderTestMixin


class OrderListTests(OrderTestMixin, APITestCase):
    def test_customer_can_list_own_orders(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.orders_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.order.id)

    def test_business_user_can_list_received_orders(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.get(self.orders_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["business_user"], self.business.id)

    def test_unrelated_customer_cannot_see_other_orders(self):
        self.client.force_authenticate(user=self.other_customer)

        response = self.client.get(self.orders_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_anonymous_user_cannot_list_orders(self):
        response = self.client.get(self.orders_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderCreateTests(OrderTestMixin, APITestCase):
    def test_customer_can_create_order_from_offer_detail(self):
        self.client.force_authenticate(user=self.customer)
        order_count = Order.objects.count()

        response = self.client.post(
            self.orders_url(),
            self.get_create_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), order_count + 1)

    def test_created_order_belongs_to_authenticated_customer(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            self.orders_url(),
            self.get_create_payload(),
            format="json",
        )

        self.assertEqual(response.data["customer_user"], self.customer.id)
        self.assertEqual(response.data["business_user"], self.business.id)

    def test_created_order_copies_offer_detail_data(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            self.orders_url(),
            self.get_create_payload(),
            format="json",
        )

        self.assertEqual(response.data["title"], self.basic_detail.title)
        self.assertEqual(response.data["revisions"], self.basic_detail.revisions)
        self.assertEqual(float(response.data["price"]), 150.0)
        self.assertEqual(response.data["offer_type"], self.basic_detail.offer_type)

    def test_created_order_starts_in_progress(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            self.orders_url(),
            self.get_create_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Order.IN_PROGRESS)

    def test_business_user_cannot_create_order(self):
        self.client.force_authenticate(user=self.business)
        order_count = Order.objects.count()

        response = self.client.post(
            self.orders_url(),
            self.get_create_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Order.objects.count(), order_count)

    def test_anonymous_user_cannot_create_order(self):
        order_count = Order.objects.count()

        response = self.client.post(
            self.orders_url(),
            self.get_create_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Order.objects.count(), order_count)

    def test_create_order_requires_offer_detail_id(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(self.orders_url(), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_returns_404_for_unknown_offer_detail(self):
        self.client.force_authenticate(user=self.customer)
        payload = {"offer_detail_id": 99999}

        response = self.client.post(self.orders_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)