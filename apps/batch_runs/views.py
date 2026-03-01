from django.views.generic import ListView, DetailView
from .models import BatchRun, CandidateAttempt


class BatchRunListView(ListView):
    model = BatchRun
    template_name = "batch_runs/list.html"
    context_object_name = "batch_runs"


class BatchRunDetailView(DetailView):
    model = BatchRun
    template_name = "batch_runs/detail.html"
    context_object_name = "batch_run"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # include related candidate attempts
        context["attempts"] = CandidateAttempt.objects.filter(batch_run=self.object)
        return context


class CandidateAttemptListView(ListView):
    model = CandidateAttempt
    template_name = "batch_runs/attempts.html"
    context_object_name = "attempts"
