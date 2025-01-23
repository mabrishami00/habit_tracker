from django.urls import path, include
from rest_framework.routers import DefaultRouter
from main_app.api.habit import HabbitView
from main_app.api.user import UserRegisterView, UserLoginView, UserGetNewTokens

router = DefaultRouter()
router.register(r"habits", HabbitView, basename="habits")


urlpatterns = [
    path("", include(router.urls)),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("refresh/", UserGetNewTokens.as_view(), name="refresh"),
]
