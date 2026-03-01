from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Candidate
from .forms import CandidateForm
from apps.core.permissions import role_required


@login_required
@role_required("ADMIN")
def candidate_edit(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)

    if request.method == "POST":
        form = CandidateForm(request.POST, instance=candidate)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = CandidateForm(instance=candidate)

    return render(request, "candidates/edit.html", {"form": form})


@login_required
@role_required("ADMIN")
def candidate_create(request):

    if request.method == "POST":
        form = CandidateForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("dashboard")

    else:
        form = CandidateForm()

    return render(request, "candidates/create.html", {"form": form})
