from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserSignupForm, LoginForm
from django.contrib.auth import authenticate, login, logout


def health(request):
    return JsonResponse({"status": "ok"})


def signup_view(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully.")
            return redirect("login")
    else:
        form = UserSignupForm()

    return render(request, "users/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                email=email,
                password=password,
            )

            if user is not None:
                login(request, user)
                messages.success(request, "Logged in successfully.")
                return redirect("dashboard")

            messages.error(request, "Invalid email or password.")

    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")
