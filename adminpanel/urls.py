from django.urls import path
from .views import (
    test,
    AdminListDB,
    ShowLogDB,
    AdminDBObjectChange,
    AdminDBObjectCreate,
    AdminDBObjectDelete,
    AdminDBObjectHistory,
)

urlpatterns = [
    path("test/", test, name="test-page"),
    path("", test, name="adminMainPage"),
    path("apps/<str:db>/", AdminListDB.as_view(), name="adminListDB"),
    path("logs/", ShowLogDB.as_view(), name="adminListLogs"),
    path(
        "apps/<str:db>/object/<pk>/",
        AdminDBObjectChange.as_view(),
        name="adminDBObject",
    ),
    path(
        "apps/<str:db>/create/",
        AdminDBObjectCreate.as_view(),
        name="adminDBObjectCreate",
    ),
    path(
        "apps/<str:db>/object/<pk>/delete/",
        AdminDBObjectDelete.as_view(),
        name="adminDBObjectDelete",
    ),
    path(
        "apps/<str:db>/object/<pk>/history/",
        AdminDBObjectHistory.as_view(),
        name="adminDBObjectHistory",
    ),
]
