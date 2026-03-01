from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.candidate_create, name="candidate_create"),
    path("<uuid:pk>/edit/", views.candidate_edit, name="candidate_edit"),
]
