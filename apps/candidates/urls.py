from django.urls import path
from . import views

urlpatterns = [
    path("candidates/", views.list_candidates, name="list_candidates"),
]
