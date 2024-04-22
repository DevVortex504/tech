from django.contrib import admin
from .models import User, Favourite

# Register your models here.
admin.site.register(User)
admin.site.register(Favourite)