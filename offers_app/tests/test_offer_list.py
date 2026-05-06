from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer

from .helpers import OfferTestMixin


class OfferListTests(OfferTestMixin, APITestCase):
    def test_authenticated_user_can_list_offers(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.offers_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 1)

    def test_anonymous_user_cannot_list_offers(self):
        response = self.client.get(self.offers_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_offer_list_contains_expected_offer_fields(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.offers_url())
        result = self.get_results(response)[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result["id"], self.offer.id)
        self.assertEqual(result["user"], self.business.id)
        self.assertEqual(result["title"], "Logo Design")
        self.assertIn("details", result)
        self.assertIn("min_price", result)
        self.assertIn("min_delivery_time", result)
        self.assertIn("user_details", result)

    def test_offer_list_contains_min_price_and_min_delivery_time(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.offers_url())
        result = self.get_results(response)[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(result["min_price"]), 100.0)
        self.assertEqual(result["min_delivery_time"], 5)

    def test_offer_list_contains_user_details(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.offers_url())
        result = self.get_results(response)[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            result["user_details"]["username"],
            self.business.username,
        )
        self.assertEqual(
            result["user_details"]["first_name"],
            self.business.first_name,
        )
        self.assertEqual(
            result["user_details"]["last_name"],
            self.business.last_name,
        )

    def test_offer_list_contains_detail_links(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.offers_url())
        result = self.get_results(response)[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(result["details"]), 3)
        self.assertIn("id", result["details"][0])
        self.assertIn("url", result["details"][0])
        self.assertTrue(
            result["details"][0]["url"].startswith("/api/offerdetails/")
        )

    def test_offer_list_can_be_filtered_by_creator_id(self):
        other_offer = self.create_offer(
            user=self.other_business,
            title="Translation Service",
            prices=[50, 100, 200],
            delivery_times=[2, 4, 6],
        )
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            self.offers_url(),
            {"creator_id": self.other_business.id},
        )
        result = self.get_results(response)[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(result["id"], other_offer.id)
        self.assertEqual(result["user"], self.other_business.id)

    def test_offer_list_can_be_filtered_by_min_price(self):
        cheap_offer = self.create_offer(
            user=self.other_business,
            title="Cheap Translation",
            prices=[10, 20, 30],
            delivery_times=[2, 4, 6],
        )
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.offers_url(), {"min_price": 100})
        result_ids = [result["id"] for result in self.get_results(response)]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.offer.id, result_ids)
        self.assertNotIn(cheap_offer.id, result_ids)

    def test_offer_list_can_be_filtered_by_max_delivery_time(self):
        slow_offer = self.create_offer(
            user=self.other_business,
            title="Slow Enterprise Design",
            prices=[300, 600, 1000],
            delivery_times=[20, 30, 40],
        )
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            self.offers_url(),
            {"max_delivery_time": 5},
        )
        result_ids = [result["id"] for result in self.get_results(response)]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.offer.id, result_ids)
        self.assertNotIn(slow_offer.id, result_ids)

    def test_offer_list_can_be_searched_by_title(self):
        translation_offer = self.create_offer(
            user=self.other_business,
            title="Translation Service",
            prices=[50, 100, 200],
            delivery_times=[2, 4, 6],
        )
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.offers_url(), {"search": "Logo"})
        result_ids = [result["id"] for result in self.get_results(response)]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.offer.id, result_ids)
        self.assertNotIn(translation_offer.id, result_ids)

    def test_offer_list_can_be_ordered_by_updated_at(self):
        other_offer = self.create_offer(
            user=self.other_business,
            title="Translation Service",
            prices=[50, 100, 200],
            delivery_times=[2, 4, 6],
        )
        old_time = timezone.now() - timedelta(days=2)
        new_time = timezone.now() - timedelta(days=1)

        Offer.objects.filter(id=self.offer.id).update(updated_at=old_time)
        Offer.objects.filter(id=other_offer.id).update(updated_at=new_time)

        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            self.offers_url(),
            {"ordering": "updated_at"},
        )
        results = self.get_results(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results[0]["id"], self.offer.id)
        self.assertEqual(results[1]["id"], other_offer.id)

    def test_offer_list_can_be_ordered_by_min_price(self):
        cheap_offer = self.create_offer(
            user=self.other_business,
            title="Cheap Translation",
            prices=[10, 20, 30],
            delivery_times=[2, 4, 6],
        )
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            self.offers_url(),
            {"ordering": "min_price"},
        )
        results = self.get_results(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results[0]["id"], cheap_offer.id)
        self.assertEqual(results[1]["id"], self.offer.id)