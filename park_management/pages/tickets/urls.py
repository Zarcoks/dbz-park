from django.urls import path

from . import views

urlpatterns = [
    path("", views.TicketList.as_view(), name="tickets"),
    path("billets/assigner/", views.TicketAssign.as_view(), name="assign_ticket"),
]
