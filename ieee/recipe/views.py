from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from django.db import IntegrityError
import requests

# Create your views here.
def index(request):
    return render(request, "recipe/index.html")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.warning(request, "Invalid username and/or password.")
            return render(request, "recipe/login.html")
    else:
        return render(request, "recipe/login.html")

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out.")
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.warning(request, "Passwords must match.")
            return render(request, "recipe/register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            
            messages.warning(request, "Username already taken.")
            return render(request, "recipe/register.html")
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "recipe/register.html")
    
