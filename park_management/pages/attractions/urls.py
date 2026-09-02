from django.urls import path

from . import views

urlpatterns = [
    path("", views.AttractionList.as_view(), name="attractions"),
]
