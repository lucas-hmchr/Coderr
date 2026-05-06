from rest_framework.permissions import BasePermission

from profiles_app.models import UserProfile


class IsCustomerUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.type == UserProfile.CUSTOMER
        )


class IsOrderBusinessUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.type == UserProfile.BUSINESS
            and obj.business_user == request.user
        )