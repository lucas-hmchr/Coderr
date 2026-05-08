from django.contrib.auth.models import User

from profiles_app.models import UserProfile
from reviews_app.models import Review


class ReviewTestMixin:
    def setUp(self):
        self.customer = self.create_user(
            username="customer_user",
            user_type=UserProfile.CUSTOMER,
        )
        self.other_customer = self.create_user(
            username="other_customer",
            user_type=UserProfile.CUSTOMER,
        )
        self.business = self.create_user(
            username="business_user",
            user_type=UserProfile.BUSINESS,
        )
        self.other_business = self.create_user(
            username="other_business",
            user_type=UserProfile.BUSINESS,
        )
        self.review = self.create_review(
            business_user=self.business,
            reviewer=self.customer,
            rating=4,
            description="Great service.",
        )

    def create_user(self, username, user_type):
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="testpass123",
        )
        UserProfile.objects.create(user=user, type=user_type)

        return user

    def create_review(self, business_user, reviewer, rating, description):
        return Review.objects.create(
            business_user=business_user,
            reviewer=reviewer,
            rating=rating,
            description=description,
        )

    def reviews_url(self):
        return "/api/reviews/"

    def review_url(self, review):
        return f"/api/reviews/{review.id}/"

    def valid_payload(self, business_user=None):
        if business_user is None:
            business_user = self.other_business

        return {
            "business_user": business_user.id,
            "rating": 5,
            "description": "Excellent work.",
        }

    def get_results(self, response):
        if isinstance(response.data, dict) and "results" in response.data:
            return response.data["results"]

        return response.data