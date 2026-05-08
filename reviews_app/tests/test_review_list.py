from rest_framework import status
from rest_framework.test import APITestCase

from .helpers import ReviewTestMixin


class ReviewListTests(ReviewTestMixin, APITestCase):
    def test_authenticated_user_can_list_reviews(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.reviews_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.get_results(response)), 1)

    def test_business_user_can_list_reviews(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.get(self.reviews_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.get_results(response)), 1)

    def test_anonymous_user_cannot_list_reviews(self):
        response = self.client.get(self.reviews_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_review_list_contains_expected_fields(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.reviews_url())
        review_data = self.get_results(response)[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", review_data)
        self.assertIn("business_user", review_data)
        self.assertIn("reviewer", review_data)
        self.assertIn("rating", review_data)
        self.assertIn("description", review_data)
        self.assertIn("created_at", review_data)
        self.assertIn("updated_at", review_data)

    def test_review_list_can_filter_by_business_user_id(self):
        other_review = self.create_review(
            business_user=self.other_business,
            reviewer=self.other_customer,
            rating=5,
            description="Excellent.",
        )
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            self.reviews_url(),
            {"business_user_id": self.other_business.id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.get_results(response)), 1)
        self.assertEqual(self.get_results(response)[0]["id"], other_review.id)

    def test_review_list_can_filter_by_reviewer_id(self):
        other_review = self.create_review(
            business_user=self.other_business,
            reviewer=self.other_customer,
            rating=5,
            description="Excellent.",
        )
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            self.reviews_url(),
            {"reviewer_id": self.other_customer.id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.get_results(response)), 1)
        self.assertEqual(self.get_results(response)[0]["id"], other_review.id)

    def test_review_list_can_order_by_rating(self):
        self.create_review(
            business_user=self.other_business,
            reviewer=self.other_customer,
            rating=2,
            description="Okay.",
        )
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.reviews_url(), {"ordering": "rating"})
        ratings = [review["rating"] for review in self.get_results(response)]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ratings, sorted(ratings))

    def test_review_list_can_order_by_updated_at_descending(self):
        self.create_review(
            business_user=self.other_business,
            reviewer=self.other_customer,
            rating=2,
            description="Okay.",
        )
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            self.reviews_url(),
            {"ordering": "-updated_at"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.get_results(response)), 2)