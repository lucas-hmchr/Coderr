from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("auth_app.api.urls")),
    path("api/profiles/", include("profiles_app.api.urls")),
    # path("api/projects/", include("orders_app.api.urls")),
    # path("api/offers/", include("offers_app.api.urls")),
    # path("api/reviews/", include("reviews_app.api.urls")),
]