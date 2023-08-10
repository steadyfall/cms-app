from django.shortcuts import render, redirect

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
                return redirect("signin")  # successful
            else:
                messages.error(request, "Wrong password. Try again.")
                return redirect("signin")
        else:
            messages.error(request, error)
            return redirect("signin")

    return render(request, "auth/signin.html")


def signout(request):
    if not request.user.is_authenticated:
        return redirect("signin") # logout
    auth.logout(request)
    return render(request, "auth/signout.html")
