from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail

from .helpers import OfferTestMixin


class OfferCreateTests(OfferTestMixin, APITestCase):
    def test_business_user_can_create_offer(self):
        self.client.force_authenticate(user=self.business)
        offer_count = Offer.objects.count()

        response = self.client.post(
            self.offers_url(),
            self.get_valid_offer_payload(),
            format="json",
        )
        created_offer = Offer.objects.order_by("-id").first()
        offer_types = set(
            created_offer.details.values_list("offer_type", flat=True)
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), offer_count + 1)
        self.assertEqual(created_offer.user, self.business)
        self.assertEqual(created_offer.details.count(), 3)
        self.assertEqual(
            offer_types,
            {
                OfferDetail.BASIC,
                OfferDetail.STANDARD,
                OfferDetail.PREMIUM,
            },
        )

    def test_created_offer_response_contains_details(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.post(
            self.offers_url(),
            self.get_valid_offer_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Website Design")
        self.assertIn("details", response.data)
        self.assertEqual(len(response.data["details"]), 3)
        self.assertEqual(response.data["details"][0]["offer_type"], "basic")

    def test_customer_user_cannot_create_offer(self):
        self.client.force_authenticate(user=self.customer)
        offer_count = Offer.objects.count()

        response = self.client.post(
            self.offers_url(),
            self.get_valid_offer_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Offer.objects.count(), offer_count)

    def test_anonymous_user_cannot_create_offer(self):
        offer_count = Offer.objects.count()

        response = self.client.post(
            self.offers_url(),
            self.get_valid_offer_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Offer.objects.count(), offer_count)

    def test_create_offer_requires_exactly_three_details(self):
        self.client.force_authenticate(user=self.business)
        payload = self.get_valid_offer_payload()
        payload["details"] = payload["details"][:2]

        response = self.client.post(
            self.offers_url(),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_offer_requires_basic_standard_and_premium(self):
        self.client.force_authenticate(user=self.business)
        payload = self.get_valid_offer_payload()
        payload["details"][2]["offer_type"] = "basic"

        response = self.client.post(
            self.offers_url(),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_offer_does_not_create_database_entries(self):
        self.client.force_authenticate(user=self.business)
        offer_count = Offer.objects.count()
        detail_count = OfferDetail.objects.count()
        payload = self.get_valid_offer_payload()
        payload["details"] = payload["details"][:1]

        response = self.client.post(
            self.offers_url(),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Offer.objects.count(), offer_count)
        self.assertEqual(OfferDetail.objects.count(), detail_count)