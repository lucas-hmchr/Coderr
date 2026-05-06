from rest_framework.permissions import BasePermission, SAFE_METHODS

from profiles_app.models import UserProfile


class IsBusinessUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return hasattr(request.user, "profile") and (
            request.user.profile.type == UserProfile.BUSINESS
        )


class IsOfferOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.user == request.user