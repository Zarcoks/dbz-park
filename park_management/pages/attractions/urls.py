from django.urls import path

from . import views

urlpatterns = [
    path("", views.AttractionList.as_view(), name="attractions"),
    path("<int:attraction_id>/file/rejoindre/", views.QueueJoin.as_view(), name="join_queue"),
    path("file/<int:entry_id>/valider/", views.QueueValidate.as_view(), name="validate_queue_entry"),
    path("file/<int:entry_id>/quitter/", views.QueueLeave.as_view(), name="leave_queue"),
]
