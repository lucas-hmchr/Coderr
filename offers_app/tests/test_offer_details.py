from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import OfferDetail

from .helpers import OfferTestMixin


class OfferUpdateDeleteTests(OfferTestMixin, APITestCase):
    def test_owner_can_patch_offer_title(self):
        self.client.force_authenticate(user=self.business)
        payload = {"title": "Updated Logo Design"}

        response = self.client.patch(
            self.offer_url(self.offer),
            payload,
            format="json",
        )
        self.offer.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.offer.title, "Updated Logo Design")

    def test_owner_can_patch_offer_with_all_details(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.patch(
            self.offer_url(self.offer),
            self.get_full_update_payload(),
            format="json",
        )
        self.offer.refresh_from_db()
        basic_detail = self.offer.details.get(offer_type=OfferDetail.BASIC)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.offer.title, "Updated Logo Design")
        self.assertEqual(basic_detail.title, "Updated Basic")
        self.assertEqual(float(basic_detail.price), 120.0)
        self.assertEqual(basic_detail.delivery_time_in_days, 4)

    def test_other_business_user_cannot_patch_offer(self):
        self.client.force_authenticate(user=self.other_business)
        payload = {"title": "Hacked Offer"}

        response = self.client.patch(
            self.offer_url(self.offer),
            payload,
            format="json",
        )
        self.offer.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.offer.title, "Logo Design")

    def test_customer_user_cannot_patch_offer(self):
        self.client.force_authenticate(user=self.customer)
        payload = {"title": "Customer Update"}

        response = self.client.patch(
            self.offer_url(self.offer),
            payload,
            format="json",
        )
        self.offer.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.offer.title, "Logo Design")

    def test_owner_can_delete_offer(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.delete(self.offer_url(self.offer))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            self.offer.__class__.objects.filter(id=self.offer.id).exists()
        )

    def test_other_business_user_cannot_delete_offer(self):
        self.client.force_authenticate(user=self.other_business)

        response = self.client.delete(self.offer_url(self.offer))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            self.offer.__class__.objects.filter(id=self.offer.id).exists()
        )

    def test_customer_user_cannot_delete_offer(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.delete(self.offer_url(self.offer))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            self.offer.__class__.objects.filter(id=self.offer.id).exists()
        )