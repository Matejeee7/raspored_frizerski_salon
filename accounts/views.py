# accounts/views.py
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages

def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # kreira usera s username + password
            # auto login nakon registracije (po želji)
            raw_username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(request, username=raw_username, password=raw_password)
            if user is not None:
                login(request, user)
                messages.success(request, "Dobrodošli! Račun je kreiran i prijavljeni ste.")
                return redirect("calendar_today")
            messages.info(request, "Račun je kreiran. Prijavite se.")
            return redirect("login")
        else:
            messages.error(request, "Provjerite unesene podatke.")
    else:
        form = UserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_GET

@require_GET
def quick_logout(request):
    logout(request)
    messages.info(request, "Odjavljeni ste.")
    return redirect("login")

