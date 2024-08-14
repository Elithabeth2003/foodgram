from django.urls import path

from .views import redirect_to_recipe_detail

app_name = 'recipes'

urlpatterns = [
    path('s/<int:pk>/', redirect_to_recipe_detail, name='shortlink'),
]
