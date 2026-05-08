from django.db.models import Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from offers_app.models import Offer
from reviews_app.models import Review
from profiles_app.models import UserProfile

class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "review_count": self.get_review_count(),
                "average_rating": self.get_average_rating(),
                "business_profile_count": self.get_business_profile_count(),
                "offer_count": self.get_offer_count(),
            }
        )

    def get_review_count(self):
        return Review.objects.count()

    def get_average_rating(self):
        average = Review.objects.aggregate(Avg("rating"))["rating__avg"]

        if average is None:
            return 0.0

        return round(average, 1)

    def get_business_profile_count(self):
        return UserProfile.objects.filter(type=UserProfile.BUSINESS).count()

    def get_offer_count(self):
        return Offer.objects.count()


