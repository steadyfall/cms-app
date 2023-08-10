from django.urls import path
from .views import test, signin, signout

urlpatterns = [
    path("test/", test, name="test-page"),
    path("signin/", signin, name="signin"),
    path("signout/", signout, name="signout"),
]