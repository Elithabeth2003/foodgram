from django.urls import path
from django.shortcuts import get_object_or_404, redirect
from .models import Recipe

app_name = 'recipes'


def redirect_to_recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return redirect('api:recipes-detail', pk=recipe.pk)


urlpatterns = [
    path('s/<int:pk>/', redirect_to_recipe_detail, name='shortlink'),
]
