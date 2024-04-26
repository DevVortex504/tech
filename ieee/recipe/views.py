from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Favourite
from django.db import IntegrityError
import requests
import json

'''
class SearchForm(forms.Form):
    q = forms.CharField(min_length=0, 
                        max_length=100, 
                        widget=forms.TextInput(attrs={'placeholder': 'Search','class':'search'}),
                        )
'''

#API KEY
API_KEY = r"2nnbadeG+8QiCVOaQXVhZw==rlBiBudZ8JUPkOB9"

# Create your views here.
def index(request):
    base_url = "https://www.themealdb.com/api/json/v1/1/categories.php"
    random_url = "https://www.themealdb.com/api/json/v1/1/random.php"
    response_random = requests.get(random_url)
    j=response_random.json()
    random = j["meals"][0]
    print(random)
    response = requests.get(base_url)
    #print(json.dumps(response.json(), indent=3))
    o=response.json()
    category = o["categories"]
    #print(category)
    return render(request, "recipe/index.html",{
        "categories" : category,
        "random": random,
    })

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
            return render(request, "recipe/login.html",{
                "username":username,
                "password":password,
            })
    else:
        return render(request, "recipe/login.html")

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out.")
    return HttpResponseRedirect(reverse("index"))


def register(request):
    username = ""
    email = ""
    password = ""
    confirmation = ""
    
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
            return render(request, "recipe/register.html",{
                "username":username,
                "email":email,
                "password":password,
                "confirmation":confirmation,
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "recipe/register.html",{
                "username":username,
                "email":email,
                "password":password,
                "confirmation":confirmation,
            })
    
def search(request, query=None):
    ...

def category(request, category=None):
    if category:
        url = "https://www.themealdb.com/api/json/v1/1/filter.php?c="+str(category)
        response = requests.get(url)
        o = response.json()
        meal = o["meals"]
        try:
            n = len(meal)
        except:
            n = 0
        return render(request,"recipe/results.html",{
            "name": category,
            "meals":meal,
            "n":n,
        })
    else:
        return HttpResponseRedirect(reverse("index"))
    

def recipe(request, id=None):
    favourite = None
    if request.user.is_authenticated:
        try:
            favourite = Favourite.objects.get(user = request.user, meal_id = int(id))
        except:
            favourite = None
    print(id)
    if not id:
        return HttpResponseRedirect(reverse("index"))
    base_url="https://www.themealdb.com/api/json/v1/1/lookup.php?i={}".format(id)
    response = requests.get(base_url)
    o = response.json()
    meal = o["meals"][0]
    ingredients = []
    for i in range(1,21):
        if meal[f"strIngredient{i}"] != "" or meal[f"strIngredient{i}"] != "null":
            name = meal[f"strIngredient{i}"]
            quantity = meal[f"strMeasure{i}"]
            ingredient = [name,quantity]
            ingredients.append(ingredient)
        else:
            break
    print(ingredients)
    return render(request, "recipe/recipe.html",{
        "meal": meal,
        "ingredients":ingredients,
        "favourite":favourite,
    })

def recipe_data(request):
    if query := request.GET.get("q"):
        base_url = "https://www.themealdb.com/api/json/v1/1/search.php?s={}".format(query)
        response = requests.get(base_url)
        #print(json.dumps(response.json(), indent=3))
        o = response.json()
        if meals:=o["meals"]:
            for meal in meals:
                print(meal["strMeal"], meal["strMealThumb"])
            #strMealThumb = image link
            #strCategory, strInstruction, idMeal
        else:
            api_url = "https://api.api-ninjas.com/v1/recipe?query={}".format(query)
            response = requests.get(api_url, headers={'X-Api-Key': API_KEY})
            if response.status_code == requests.codes.ok:
                print(json.dumps(response.json(), indent=3))
                for meal in response.json():
                    print(meal["title"])
            else:
                return HttpResponse(f"Error: {response.status_code} {response.text}")  
    print(json.dumps(meals, indent=3))
    try:
        n = len(meals)
    except:
        n = 0
    return render(request, "recipe/results.html",{
        "meals": meals,
        "query": query,
        "n":n,
    })

@login_required
def favourite(request):
    meals = []
    base_url = "https://www.themealdb.com/api/json/v1/1/lookup.php?i="
    id = []
    favourites = Favourite.objects.filter(user = request.user).all()
    for favourite in favourites:
        id = int(favourite.meal_id)
        response = requests.get(base_url+str(id))
        o = response.json()
        meal = o["meals"][0]
        meals.append(meal)
    try:
        n = len(meals)
    except:
        n = 0
    print(meals)
    return render(request, "recipe/favourites.html",{
        "favourites": favourite,
        "meals": meals,
        "n":n
    })

@login_required
def favourite_add(request, meal_id):
    meal_id = meal_id
    user = request.user
    if Favourite.objects.filter(user=user, meal_id=meal_id):
        messages.warning(request, "Meal already Favourited.")
    else:
        favourite = Favourite(user=user, meal_id=meal_id)
        favourite.save()
        messages.success(request,"Added to Favourites.")
    return redirect("recipe", id = meal_id)

@login_required
def favourite_remove(request, meal_id):
    favourite = Favourite.objects.get(user=request.user, meal_id=int(meal_id))
    favourite.delete()
    messages.success(request,"Removed from Favourites")
    return redirect("recipe", id = meal_id)

