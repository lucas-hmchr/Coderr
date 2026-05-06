from rest_framework import status
from rest_framework.test import APITestCase

from .helpers import OfferTestMixin


class OfferRetrieveTests(OfferTestMixin, APITestCase):
    def test_authenticated_user_can_retrieve_offer(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.offer_url(self.offer))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.offer.id)
        self.assertEqual(response.data["title"], self.offer.title)
        self.assertEqual(response.data["user"], self.business.id)

    def test_retrieved_offer_contains_detail_links(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.offer_url(self.offer))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("details", response.data)
        self.assertEqual(len(response.data["details"]), 3)
        self.assertIn("id", response.data["details"][0])
        self.assertIn("url", response.data["details"][0])

    def test_retrieved_offer_contains_summary_values(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.offer_url(self.offer))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data["min_price"]), 100.0)
        self.assertEqual(response.data["min_delivery_time"], 5)

    def test_anonymous_user_cannot_retrieve_offer(self):
        response = self.client.get(self.offer_url(self.offer))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_unknown_offer_returns_404(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get("/api/offers/99999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)