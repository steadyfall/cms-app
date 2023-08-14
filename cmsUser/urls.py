from django.urls import path, include
from .views import MainPage, ChangeRecord

urlpatterns = [
    path("", MainPage.as_view(), name="MainPage"),
    path("change-records/", ChangeRecord.as_view(), name="MainPage"),
]
