from django.urls import path

from . import views

urlpatterns = [
    path("", views.Console.as_view(), name="console"),
    path("file/<int:entry_id>/accepter/", views.AcceptEntry.as_view(), name="accept_queue_entry"),
    path("file/<int:entry_id>/refuser/", views.RefuseEntry.as_view(), name="refuse_queue_entry"),
]
