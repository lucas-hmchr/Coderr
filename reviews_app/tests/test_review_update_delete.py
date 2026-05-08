from rest_framework import status
from rest_framework.test import APITestCase

from reviews_app.models import Review

from .helpers import ReviewTestMixin


class ReviewUpdateTests(ReviewTestMixin, APITestCase):
    def test_owner_can_update_review_rating(self):
        self.client.force_authenticate(user=self.customer)
        payload = {"rating": 5}

        response = self.client.patch(
            self.review_url(self.review),
            payload,
            format="json",
        )
        self.review.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.review.rating, 5)

    def test_owner_can_update_review_description(self):
        self.client.force_authenticate(user=self.customer)
        payload = {"description": "Updated review."}

        response = self.client.patch(
            self.review_url(self.review),
            payload,
            format="json",
        )
        self.review.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.review.description, "Updated review.")

    def test_other_customer_cannot_update_review(self):
        self.client.force_authenticate(user=self.other_customer)
        payload = {"rating": 1}

        response = self.client.patch(
            self.review_url(self.review),
            payload,
            format="json",
        )
        self.review.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.review.rating, 4)

    def test_business_user_cannot_update_review(self):
        self.client.force_authenticate(user=self.business)
        payload = {"rating": 1}

        response = self.client.patch(
            self.review_url(self.review),
            payload,
            format="json",
        )
        self.review.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.review.rating, 4)

    def test_anonymous_user_cannot_update_review(self):
        payload = {"rating": 5}

        response = self.client.patch(
            self.review_url(self.review),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_review_rejects_invalid_rating(self):
        self.client.force_authenticate(user=self.customer)
        payload = {"rating": 6}

        response = self.client.patch(
            self.review_url(self.review),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_review_ignores_business_user_change(self):
        self.client.force_authenticate(user=self.customer)
        payload = {
            "business_user": self.other_business.id,
            "rating": 5,
        }

        response = self.client.patch(
            self.review_url(self.review),
            payload,
            format="json",
        )
        self.review.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.review.business_user, self.business)


class ReviewDeleteTests(ReviewTestMixin, APITestCase):
    def test_owner_can_delete_review(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.delete(self.review_url(self.review))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())

    def test_other_customer_cannot_delete_review(self):
        self.client.force_authenticate(user=self.other_customer)

        response = self.client.delete(self.review_url(self.review))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Review.objects.filter(id=self.review.id).exists())

    def test_business_user_cannot_delete_review(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.delete(self.review_url(self.review))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Review.objects.filter(id=self.review.id).exists())

    def test_anonymous_user_cannot_delete_review(self):
        response = self.client.delete(self.review_url(self.review))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Review.objects.filter(id=self.review.id).exists())