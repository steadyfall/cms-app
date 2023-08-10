from django.urls import path
from .views import test, signin, signout, admin_signin, admin_signout

urlpatterns = [
    path("test/", test, name="test-page"),
    path("signin/", signin, name="signin"),
    path("signout/", signout, name="signout"),
    path("admin-signin/", admin_signin, name="admin-signin"),
    path("admin-signout/", admin_signout, name="admin-signout"),
]