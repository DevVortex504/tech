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
]