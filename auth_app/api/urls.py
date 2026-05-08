from django.urls import path

from .views import LoginView, RegistrationView

urlpatterns = [
    path("auth/registration/", RegistrationView.as_view(), name="registration"),
    path("auth/login/", LoginView.as_view(), name="login"),
]