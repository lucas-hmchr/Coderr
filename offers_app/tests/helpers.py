from django.contrib.auth.models import User

from offers_app.models import Offer, OfferDetail
from profiles_app.models import UserProfile


class OfferTestMixin:
    def setUp(self):
        self.customer = self.create_user(
            username="customer_user",
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
        self.offer = self.create_offer(
            user=self.business,
            title="Logo Design",
            prices=[100, 200, 500],
            delivery_times=[5, 7, 10],
        )

    def create_user(self, username, user_type):
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="testpass123",
            first_name=username,
            last_name="Test",
        )
        UserProfile.objects.create(user=user, type=user_type)

        return user

    def create_offer(self, user, title, prices, delivery_times):
        offer = Offer.objects.create(
            user=user,
            title=title,
            description=f"{title} description",
        )
        self.create_offer_details(offer, prices, delivery_times)

        return offer

    def create_offer_details(self, offer, prices, delivery_times):
        offer_types = [
            OfferDetail.BASIC,
            OfferDetail.STANDARD,
            OfferDetail.PREMIUM,
        ]

        for index, offer_type in enumerate(offer_types):
            OfferDetail.objects.create(
                offer=offer,
                title=f"{offer_type.title()} Package",
                revisions=index + 1,
                delivery_time_in_days=delivery_times[index],
                price=prices[index],
                features=[f"{offer_type} feature"],
                offer_type=offer_type,
            )

    def get_valid_offer_payload(self):
        return {
            "title": "Website Design",
            "description": "Professional website design package.",
            "details": [
                {
                    "title": "Basic Website",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100.0,
                    "features": ["Landing page"],
                    "offer_type": "basic",
                },
                {
                    "title": "Standard Website",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 200.0,
                    "features": ["Landing page", "Contact form"],
                    "offer_type": "standard",
                },
                {
                    "title": "Premium Website",
                    "revisions": 10,
                    "delivery_time_in_days": 10,
                    "price": 500.0,
                    "features": ["Landing page", "Shop", "SEO"],
                    "offer_type": "premium",
                },
            ],
        }

    def get_full_update_payload(self):
        return {
            "title": "Updated Logo Design",
            "description": "Updated offer description.",
            "details": [
                {
                    "title": "Updated Basic",
                    "revisions": 3,
                    "delivery_time_in_days": 4,
                    "price": 120.0,
                    "features": ["Updated basic feature"],
                    "offer_type": "basic",
                },
                {
                    "title": "Updated Standard",
                    "revisions": 6,
                    "delivery_time_in_days": 6,
                    "price": 240.0,
                    "features": ["Updated standard feature"],
                    "offer_type": "standard",
                },
                {
                    "title": "Updated Premium",
                    "revisions": 12,
                    "delivery_time_in_days": 8,
                    "price": 600.0,
                    "features": ["Updated premium feature"],
                    "offer_type": "premium",
                },
            ],
        }

    def offers_url(self):
        return "/api/offers/"

    def offer_url(self, offer):
        return f"/api/offers/{offer.id}/"

    def offer_detail_url(self, detail):
        return f"/api/offerdetails/{detail.id}/"

    def get_results(self, response):
        return response.data["results"]