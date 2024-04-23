from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    #API Routes
    path("recipe/<int:id>", views.recipe, name="recipe"),
    path("api/query/", views.recipe_data, name="search"),
    path("category/<str:category>", views.category, name="category"),
    path("recipe/<int:meal_id>/favourite/", views.favourite_add, name="favourite_add"),
    path("recipe/<int:meal_id>/favourite/remove/", views.favourite_remove, name="favourite_remove"),
    path("favourites/", views.favourite, name="favourites")
]