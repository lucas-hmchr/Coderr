from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from profiles_app.models import UserProfile


class ProfileDetailTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username="customer_user",
            email="customer@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Doe",
        )
        self.business = User.objects.create_user(
            username="business_user",
            email="business@example.com",
            password="testpass123",
            first_name="Max",
            last_name="Business",
        )
        self.customer_profile = UserProfile.objects.create(
            user=self.customer,
            type=UserProfile.CUSTOMER,
        )
        self.business_profile = UserProfile.objects.create(
            user=self.business,
            type=UserProfile.BUSINESS,
            location="Berlin",
            tel="123456789",
            description="Business description",
            working_hours="9-17",
        )

    def test_authenticated_user_can_get_profile(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse("profile-detail", kwargs={"pk": self.business.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.business.id)
        self.assertEqual(response.data["username"], self.business.username)
        self.assertEqual(response.data["type"], UserProfile.BUSINESS)

    def test_anonymous_user_cannot_get_profile(self):
        url = reverse("profile-detail", kwargs={"pk": self.business.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_owner_can_update_profile(self):
        self.client.force_authenticate(user=self.business)
        url = reverse("profile-detail", kwargs={"pk": self.business.id})
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "location": "Hamburg",
            "tel": "987654321",
            "description": "Updated description",
            "working_hours": "10-18",
            "email": "updated@example.com",
        }

        response = self.client.patch(url, data, format="json")
        self.business.refresh_from_db()
        self.business_profile.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.business.first_name, data["first_name"])
        self.assertEqual(self.business.email, data["email"])
        self.assertEqual(self.business_profile.location, data["location"])

    def test_user_cannot_update_other_profile(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse("profile-detail", kwargs={"pk": self.business.id})
        data = {"location": "Munich"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ProfileListTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username="customer_user",
            email="customer@example.com",
            password="testpass123",
        )
        self.business = User.objects.create_user(
            username="business_user",
            email="business@example.com",
            password="testpass123",
        )
        UserProfile.objects.create(
            user=self.customer,
            type=UserProfile.CUSTOMER,
        )
        UserProfile.objects.create(
            user=self.business,
            type=UserProfile.BUSINESS,
        )

    def test_authenticated_user_can_get_business_profiles(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse("business-profile-list")

        response = self.client.get(url)
        results = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["type"], UserProfile.BUSINESS)

    def test_authenticated_user_can_get_customer_profiles(self):
        self.client.force_authenticate(user=self.business)
        url = reverse("customer-profile-list")

        response = self.client.get(url)
        results = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["type"], UserProfile.CUSTOMER)

    def test_anonymous_user_cannot_get_business_profiles(self):
        url = reverse("business-profile-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)