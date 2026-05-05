from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from profiles_app.models import UserProfile


class RegistrationTests(APITestCase):
    def test_user_can_register_as_customer(self):
        url = reverse("registration")
        data = {
            "username": "customer_user",
            "email": "customer@example.com",
            "password": "testpass123",
            "repeated_password": "testpass123",
            "type": "customer",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], data["username"])
        self.assertEqual(response.data["email"], data["email"])
        self.assertTrue(User.objects.filter(username=data["username"]).exists())
        self.assertTrue(
            UserProfile.objects.filter(type=UserProfile.CUSTOMER).exists()
        )

    def test_user_can_register_as_business(self):
        url = reverse("registration")
        data = {
            "username": "business_user",
            "email": "business@example.com",
            "password": "testpass123",
            "repeated_password": "testpass123",
            "type": "business",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            UserProfile.objects.filter(type=UserProfile.BUSINESS).exists()
        )

    def test_registration_fails_when_passwords_do_not_match(self):
        url = reverse("registration")
        data = {
            "username": "broken_user",
            "email": "broken@example.com",
            "password": "testpass123",
            "repeated_password": "wrongpass123",
            "type": "customer",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="broken_user").exists())


class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="login_user",
            email="login@example.com",
            password="testpass123",
        )

    def test_user_can_login(self):
        url = reverse("login")
        data = {
            "username": "login_user",
            "password": "testpass123",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["user_id"], self.user.id)
        self.assertTrue(Token.objects.filter(user=self.user).exists())

    def test_login_fails_with_wrong_credentials(self):
        url = reverse("login")
        data = {
            "username": "login_user",
            "password": "wrongpass",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)