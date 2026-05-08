from rest_framework import status
from rest_framework.test import APITestCase

from reviews_app.models import Review

from .helpers import ReviewTestMixin


class ReviewCreateTests(ReviewTestMixin, APITestCase):
    def test_customer_can_create_review(self):
        self.client.force_authenticate(user=self.customer)
        review_count = Review.objects.count()

        response = self.client.post(
            self.reviews_url(),
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), review_count + 1)

    def test_created_review_uses_authenticated_user_as_reviewer(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            self.reviews_url(),
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["reviewer"], self.customer.id)

    def test_created_review_contains_business_user(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            self.reviews_url(),
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["business_user"], self.other_business.id)

    def test_business_user_cannot_create_review(self):
        self.client.force_authenticate(user=self.business)
        review_count = Review.objects.count()

        response = self.client.post(
            self.reviews_url(),
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), review_count)

    def test_anonymous_user_cannot_create_review(self):
        review_count = Review.objects.count()

        response = self.client.post(
            self.reviews_url(),
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Review.objects.count(), review_count)

    def test_customer_cannot_review_same_business_twice(self):
        self.client.force_authenticate(user=self.customer)
        payload = self.valid_payload(business_user=self.business)

        response = self.client.post(
            self.reviews_url(),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_cannot_review_customer_user(self):
        self.client.force_authenticate(user=self.customer)
        payload = self.valid_payload(business_user=self.other_customer)

        response = self.client.post(
            self.reviews_url(),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_requires_business_user(self):
        self.client.force_authenticate(user=self.customer)
        payload = self.valid_payload()
        payload.pop("business_user")

        response = self.client.post(
            self.reviews_url(),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_rejects_rating_below_one(self):
        self.client.force_authenticate(user=self.customer)
        payload = self.valid_payload()
        payload["rating"] = 0

        response = self.client.post(
            self.reviews_url(),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_review_rejects_rating_above_five(self):
        self.client.force_authenticate(user=self.customer)
        payload = self.valid_payload()
        payload["rating"] = 6

        response = self.client.post(
            self.reviews_url(),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)