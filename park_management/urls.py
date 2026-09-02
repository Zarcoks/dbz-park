"""Routes every page of the application, one included URLconf per page."""
from django.urls import include, path

urlpatterns = [
    path("", include("park_management.pages.tickets.urls")),
    path("attractions/", include("park_management.pages.attractions.urls")),
    path("compte/", include("park_management.pages.accounts.urls")),
]
