from rest_framework import status
from rest_framework.test import APITestCase

from orders_app.models import Order

from .helpers import OrderTestMixin


class OrderUpdateTests(OrderTestMixin, APITestCase):
    def test_business_user_can_update_order_status(self):
        self.client.force_authenticate(user=self.business)
        payload = {"status": Order.COMPLETED}

        response = self.client.patch(
            self.order_url(self.order),
            payload,
            format="json",
        )
        self.order.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.order.status, Order.COMPLETED)

    def test_customer_cannot_update_order_status(self):
        self.client.force_authenticate(user=self.customer)
        payload = {"status": Order.COMPLETED}

        response = self.client.patch(
            self.order_url(self.order),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_business_cannot_update_order_status(self):
        self.client.force_authenticate(user=self.other_business)
        payload = {"status": Order.COMPLETED}

        response = self.client.patch(
            self.order_url(self.order),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_order_rejects_invalid_status(self):
        self.client.force_authenticate(user=self.business)
        payload = {"status": "unknown_status"}

        response = self.client.patch(
            self.order_url(self.order),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_rejects_non_status_fields(self):
        self.client.force_authenticate(user=self.business)
        payload = {"title": "Manipulated Title"}

        response = self.client.patch(
            self.order_url(self.order),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_user_cannot_update_order(self):
        payload = {"status": Order.COMPLETED}

        response = self.client.patch(
            self.order_url(self.order),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderDeleteTests(OrderTestMixin, APITestCase):
    def test_staff_user_can_delete_order(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.delete(self.order_url(self.order))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

    def test_business_user_cannot_delete_order(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.delete(self.order_url(self.order))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Order.objects.filter(id=self.order.id).exists())

    def test_customer_user_cannot_delete_order(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.delete(self.order_url(self.order))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Order.objects.filter(id=self.order.id).exists())

    def test_anonymous_user_cannot_delete_order(self):
        response = self.client.delete(self.order_url(self.order))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Order.objects.filter(id=self.order.id).exists())