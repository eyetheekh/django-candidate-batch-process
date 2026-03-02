from django.urls import path
from .views import BatchRunListView, BatchRunTriggerView

urlpatterns = [
    path(
        "",
        BatchRunListView.as_view(),
        name="batch-run-list",
    ),
    path(
        "trigger/",
        BatchRunTriggerView.as_view(),
        name="batch-run-trigger",
    ),
]
