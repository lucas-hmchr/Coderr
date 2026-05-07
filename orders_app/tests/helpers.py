from django.contrib.auth.models import User

from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from profiles_app.models import UserProfile


class OrderTestMixin:
    def setUp(self):
        self.customer = self.create_user("customer_user", UserProfile.CUSTOMER)
        self.other_customer = self.create_user(
            "other_customer",
            UserProfile.CUSTOMER,
        )
        self.business = self.create_user("business_user", UserProfile.BUSINESS)
        self.other_business = self.create_user(
            "other_business",
            UserProfile.BUSINESS,
        )
        self.staff_user = self.create_staff_user()
        self.offer = self.create_offer(self.business)
        self.basic_detail = self.create_offer_detail(self.offer)
        self.order = self.create_order()

    def create_user(self, username, user_type):
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="testpass123",
        )
        UserProfile.objects.create(user=user, type=user_type)

        return user

    def create_staff_user(self):
        return User.objects.create_user(
            username="staff_user",
            email="staff@example.com",
            password="testpass123",
            is_staff=True,
        )

    def create_offer(self, user):
        return Offer.objects.create(
            user=user,
            title="Logo Design",
            description="Professional logo design.",
        )

    def create_offer_detail(self, offer):
        return OfferDetail.objects.create(
            offer=offer,
            title="Basic Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price=150.0,
            features=["Logo Design", "Business Card"],
            offer_type=OfferDetail.BASIC,
        )

    def create_order(self, status=Order.IN_PROGRESS):
        return Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Basic Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price=150.0,
            features=["Logo Design", "Business Card"],
            offer_type=OfferDetail.BASIC,
            status=status,
        )

    def orders_url(self):
        return "/api/orders/"

    def order_url(self, order):
        return f"/api/orders/{order.id}/"

    def order_count_url(self, business_user):
        return f"/api/order-count/{business_user.id}/"

    def completed_order_count_url(self, business_user):
        return f"/api/completed-order-count/{business_user.id}/"

    def get_create_payload(self):
        return {"offer_detail_id": self.basic_detail.id}