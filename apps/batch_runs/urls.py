from django.urls import path
from .views import BatchRunListView, BatchRunDetailView, CandidateAttemptListView

urlpatterns = [
    path("", BatchRunListView.as_view(), name="batchrun-list"),
    path("<int:pk>/", BatchRunDetailView.as_view(), name="batchrun-detail"),
    path("attempts/", CandidateAttemptListView.as_view(), name="attempt-list"),
]
