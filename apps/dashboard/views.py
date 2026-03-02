from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from apps.candidates.models import Candidate


@login_required
def reports_dashboard(request):
    candidates_qs = Candidate.objects.all().order_by("-created_at")

    paginator = Paginator(candidates_qs, 10)
    page_number = request.GET.get("page")
    candidates_page = paginator.get_page(page_number)

    return render(
        request,
        "dashboard/index.html",
        {
            "candidates": candidates_page,
        },
    )
