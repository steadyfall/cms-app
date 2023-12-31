from django.urls import path, include
from .views import MainPage, ChangeRecord, ViewRecords

urlpatterns = [
    path("", MainPage.as_view(), name="MainPage"),
    path("change-records/", ChangeRecord.as_view(), name="changeRecord"),
    path("view-records/", ViewRecords.as_view(), name="viewRecords"),
]
