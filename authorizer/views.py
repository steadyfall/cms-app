from django.shortcuts import render, redirect, HttpResponseRedirect

from django.contrib import messages
from django.contrib.auth.models import User

from django.contrib import auth
from .validate import usernameValidator, confirmPassword, passwordValidator


def test(request):
    return render(request, "auth/signin.html")


def signin(request):
    error: str = "Data is invalid. Try again."
    if request.method == "POST":
        try:
            username: str = request.POST["username"]
            password: str = request.POST["password"]
        except KeyError:
            messages.error(request, error)
            return redirect("signin")

        check: bool = usernameValidator(username) and passwordValidator(password)
        if check:
            if not User.objects.filter(username=username).exists():
                messages.warning(
                    request,
                    "You don't have an account. Kindly check with admin before trying again.",
                )
                return redirect("signin")
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect("MainPage")  # successful
            else:
                messages.error(request, "Wrong password. Try again.")
                return redirect("signin")
        else:
            messages.error(request, error)
            return redirect("signin")

    return render(request, "auth/signin.html")


def signout(request):
    if not request.user.is_authenticated:
        return redirect("MainPage")
    auth.logout(request)
    return render(request, "auth/signout.html")


def admin_signin(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            redirect("adminMainPage")
        else:
            return redirect("MainPage") # successful but not superuser, so go back to MainPage

    error: str = "Data is invalid. Try again."
    if request.method == "POST":
        try:
            username: str = request.POST["username"]
            password: str = request.POST["password"]
        except KeyError:
            messages.error(request, error)
            return redirect("admin-signin")

        check: bool = usernameValidator(username)
        if check:
            if not User.objects.filter(username=username).exists():
                messages.warning(
                    request,
                    "You don't have an account. Contact the head administrator.",
                )
                return redirect("admin-signin")
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                if user.is_superuser:
                    return redirect("adminMainPage")
                return redirect("MainPage")
            else:
                messages.error(request, "Wrong password. Try again.")
                return redirect("admin-signin")
        else:
            messages.error(request, error)
            return redirect("admin-signin")

    return render(request, "auth/admin_signin.html")


def admin_signout(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
    auth.logout(request)
    return render(request, "auth/admin_signout.html")
