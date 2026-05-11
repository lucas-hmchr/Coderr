from rest_framework.permissions import BasePermission

from profiles_app.models import UserProfile


class IsCustomerUser(BasePermission):
    """Allows access only for customer users."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.type == UserProfile.CUSTOMER
        )


class IsReviewOwner(BasePermission):
    """Allows access only for the review owner."""
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and obj.reviewer == request.user
        )
