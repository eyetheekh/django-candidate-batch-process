from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.candidates.models import Candidate


@login_required
def reports_dashboard(request):
    candidates = Candidate.objects.all().order_by("-created_at")

    return render(
        request,
        "reports/index.html",
        {
            "candidates": candidates,
        },
    )
